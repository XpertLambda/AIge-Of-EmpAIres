import math
import pygame
from Settings.setup import MAXIMUM_CARRY, RESOURCE_RATE_PER_SEC, Resources, FRAMES_PER_UNIT, HALF_TILE_SIZE,TILE_SIZE, ALLOWED_ANGLES, ATTACK_RANGE_EPSILON, UNIT_HITBOX, villager_tasks, UNIT_ATTACKRANGE
from Entity.Unit.Unit import Unit
from AiUtils.aStar import a_star
from Controller.utils import tile_to_screen, get_direction, get_snapped_angle, normalize
from Controller.terminal_display_debug import debug_print
import random
from Controller.drawing import draw_sprite, draw_hitbox, draw_path



class Villager(Unit):
    def __init__(self, team=None, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym="v", 
            max_hp=40, 
            cost=Resources(food=50, gold=0, wood=25), 
            attack_power=2,
            attack_range=UNIT_ATTACKRANGE, 
            attack_speed=2.03,
            speed=1, 
            training_time=20, 

        )
        self.carry = Resources(food=0, gold=0, wood=0)
        self.resource_rate = RESOURCE_RATE_PER_SEC
        self.task = None
        self.collect_target = None
        self.build_target = None
        self.stock_target = None
        self.task_timer = 0

    # ---------------- Update Unit ---------------
    def update(self, game_map, dt):
        self.animator(dt)
        if self.isAlive():
            self.seekAttack(game_map, dt)
            #self.seekCollision(game_map, dt)
            self.seekCollect(game_map, dt)
            self.seekStock(game_map)
            self.seekMove(game_map, dt)
            self.seekIdle()
            self.seekBuild(game_map)
            self.seekRepair(game_map, dt)
        else:
            self.death(game_map, dt)

    # ---------------- Controller ----------------
    def seekIdle(self):
        if not self.attack_target and not self.collect_target and not self.stock_target and not self.build_target  and not self.path :
            self.state = 'idle'
            self.set_task(None)
        self.cooldown_frame = None

    def set_target(self, target):
        self.attack_target = None
        self.collect_target = None
        self.build_target = None
        self.stock_target = None
        self.set_task(None)
        self.set_destination(None, None)
        if target and target.isAlive() and target.entity_id != self.entity_id:
            if target.team == self.team and hasattr(target, 'buildTime'):
                if target.processTime < target.dynamicBuildTime:
                    self.set_task('build', target)
                
                elif hasattr(target, 'resourceDropPoint') and target.resourceDropPoint and target.state == 'idle':
                    self.set_task('stock', target)
            
            elif target.hasResources:
                if type(target).__name__ == "Farm" and not target.isBuilt():
                    return
                self.set_task('collect', target)

            elif target.team != self.team:
                self.attack_target = target

    def set_task(self, task, target = None):
        if task in villager_tasks:
            self.task = task
            setattr(self, villager_tasks[task], target)

    def isAvailable(self):
        if self.isAlive() and self.state == 'idle' :
            return True
        return False

    def seekCollect(self, game_map, dt):
        if self.task != 'collect':
            return

        if not self.collect_target or not self.collect_target.isAlive():
            self.task = 'stock'
            return
        
        corner_distance = self.collect_target.size / 2.0 
        left = self.collect_target.x - corner_distance
        right = self.collect_target.x + corner_distance
        top = self.collect_target.y - corner_distance
        bottom = self.collect_target.y + corner_distance
        closest_point = (
            max(left, min(self.x, right)),
            max(top, min(self.y, bottom))
        )
        distance = math.dist(closest_point, (self.x, self.y)) - 1

        # Stop if carrying too much or far away
        if distance > 0 or self.carry.total() >= MAXIMUM_CARRY:
            if not self.path:
                self.set_destination((self.collect_target.x, self.collect_target.y), game_map)
                self.task_timer = 0
            return
        self.state = 'task'
        # Collect resources
        self.direction = get_direction(get_snapped_angle((self.x, self.y),
                                                         (self.collect_target.x, self.collect_target.y)))

        # Initialize partial collect amount
        if self.task_timer == 0:
            self.current_frame = 0
            self.temp_collect_amount = 0
            self.set_destination(None, game_map)

        self.task_timer += dt
        self.temp_collect_amount += min(self.resource_rate * dt, abs(MAXIMUM_CARRY - self.carry.total()))
        self.path = []

        # Resource transaction
        if self.temp_collect_amount >= 1:
            collected_whole = round(self.temp_collect_amount)
            resource_collected = self.collect_target.storage.decrease_resources((collected_whole,
                                                                                 collected_whole,
                                                                                 collected_whole))
            self.collect_target.hp -= max(resource_collected)
            self.carry.increase_resources(resource_collected)
            self.temp_collect_amount = 0

        if self.carry.total() >= MAXIMUM_CARRY or not self.collect_target.isAlive():
            self.task = 'stock'

    def seekStock(self, game_map):
        if self.task != 'stock':
            return
        if self.stock_target and self.stock_target.isAlive():
            distance = math.dist((self.x, self.y), (self.stock_target.x, self.stock_target.y)) - self.stock_target.hitbox - 1
            if self.carry.total() == 0:
                    self.task = 'collect'
                    return
            if distance <= 0:
                self.state = 'idle'
                self.set_destination(None, game_map)
                self.stock_target.stock(game_map, self.carry.get())
                self.carry.reset()
            elif not self.path:
                self.set_destination((self.stock_target.x, self.stock_target.y), game_map)
       
        else :
            closest_building = None
            min_distance = float('inf')
            for building in game_map.players[self.team].buildings:
                if building.resourceDropPoint:
                    distance = math.dist((self.x, self.y),(building.x, building.y))
                    if distance < min_distance:
                        min_distance = distance
                        closest_building = building
            if closest_building:
                self.stock_target = closest_building
    
    def seekBuild(self, game_map):
        if self.task != 'build':
            return
        if not self.build_target or not self.build_target.isAlive() or self.build_target.state != 'construction':
            self.task = None
            self.build_target = None
            self.path = []
            return

        if self not in self.build_target.builders:
            self.build_target.builders.add(self)
        corner_distance = self.build_target.size / 2.0
        left = self.build_target.x - corner_distance
        right = self.build_target.x + corner_distance
        top = self.build_target.y - corner_distance
        bottom = self.build_target.y + corner_distance
        closest_point = (
            max(left, min(self.x, right)),
            max(top, min(self.y, bottom))
        )
        distance = math.dist(closest_point, (self.x, self.y)) - 1

        if distance > 0 :
            if self.path:
                self.path = [self.path[0]] + a_star((self.x, self.y), (self.build_target.x,self.build_target.y), game_map)
            else:
                self.set_destination((self.build_target.x,self.build_target.y), game_map)
        
        else:
            self.state = 'task'
            self.path = []

    def seekRepair(self, game_map, dt):
        if self.task != 'repair':
            return
        if not self.build_target or not self.build_target.isAlive() or self.build_target.hp < self.build_target.max_hp:
            self.task = None
            return

        corner_distance = self.build_target.size / 2.0
        left = self.build_target.x - corner_distance
        right = self.build_target.x + corner_distance
        top = self.build_target.y - corner_distance
        bottom = self.build_target.y + corner_distance
        closest_point = (
            max(left, min(self.x, right)),
            max(top, min(self.y, bottom))
        )
        distance = math.dist(closest_point, (self.x, self.y))

        if distance > self.attack_range:
            self.set_destination((self.build_target.x, self.build_target.y), game_map)
        else:
            self.state = 'task'
            # Simple repair logic
            repair_amount = 2 * dt
            self.build_target.hp = min(self.build_target.hp + repair_amount, self.build_target.max_hp)
            if self.build_target.hp >= self.build_target.max_hp:
                self.task = None

    '''
    def display_hitbox(self, screen, screen_width, screen_height, camera):
        corner_distance = self.size / 2.0
        corners = [
            (self.x - corner_distance, self.y - corner_distance),
            (self.x - corner_distance, self.y + corner_distance),
            (self.x + corner_distance, self.y + corner_distance),
            (self.x + corner_distance, self.y - corner_distance)
        ]
        
        screen_corners = []
        for corner in corners:
            x_screen, y_screen = tile_to_screen(
                corner[0], 
                corner[1], 
                HALF_TILE_SIZE, 
                HALF_TILE_SIZE / 2, 
                camera, 
                screen_width, 
                screen_height
            )
            screen_corners.append((x_screen, y_screen))
        
        draw_hitbox(screen, screen_corners, camera.zoom, self.hitbox_color)

        center = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        hitbox_iso = self.hitbox / math.cos(math.radians(45))
        width =  hitbox_iso * camera.zoom * HALF_TILE_SIZE
        height = hitbox_iso * camera.zoom * HALF_TILE_SIZE / 2
        x = center[0] - width // 2
        y = center[1] - height // 2 
        pygame.draw.ellipse(screen, (255, 0, 0), (x, y, width, height), 1)
        pygame.draw.rect(screen, (0, 255, 0), (x, y, width, height), 1)
        

        if self.attack_target and self.attack_target.isAlive():
            if not isinstance(self.attack_target, Unit):
                corner_distance = self.attack_target.size / 2.0
                left = self.attack_target.x - corner_distance
                right = self.attack_target.x + corner_distance
                top = self.attack_target.y - corner_distance
                bottom = self.attack_target.y + corner_distance
                closest_point = (
                    max(left, min(self.x, right)),
                    max(top, min(self.y, bottom))
                )
                distance = math.dist(closest_point, (self.x, self.y)) - self.attack_range          
            else:
                distance = math.dist((self.x, self.y), (self.attack_target.x, self.attack_target.y))
                distance -= (self.attack_target.hitbox + self.attack_range)
            if distance <= 0 :
                closest_point = tile_to_screen(closest_point[0], closest_point[1], HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
                ## DEBUG INSTRUCTIONS
                self.hitbox_color = (0, 0, 255)
                self.attack_target.hitbox_color = (0, 0, 255)
                pygame.draw.circle(screen, (0,255,0), closest_point, 5*camera.zoom, 0)

        elif self.collect_target and self.collect_target.isAlive():
            corner_distance = self.collect_target.size / 2.0
            left = self.collect_target.x - corner_distance
            right = self.collect_target.x + corner_distance
            top = self.collect_target.y - corner_distance
            bottom = self.collect_target.y + corner_distance
            closest_point = (
                max(left, min(self.x, right)),
                max(top, min(self.y, bottom))
            )
            distance = math.dist(closest_point, (self.x, self.y)) - self.attack_range          
        
            if distance <= 0 :
                closest_point = tile_to_screen(closest_point[0], closest_point[1], HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
                self.hitbox_color = (0, 0, 255)
                self.collect_target.hitbox_color = (0, 0, 255)
                pygame.draw.circle(screen, (0,255,0), closest_point, 5*camera.zoom, 0)
        '''
    '''
    def collectResource(self, resource_tile, duration, game_map):
        if not self.isAvailable():
            return
        if not isinstance(resource_tile, Resource):
            return
        self.task = 'collect'
        self.move(resource_tile.x, resource_tile.y, game_map)
        collected = min(
            self.resource_rate * duration,
            self.carry_capacity - getattr(self.resources, resource_tile.acronym.lower(), 0)
        )
        setattr(self.resources, resource_tile.acronym.lower(), getattr(self.resources, resource_tile.acronym.lower(), 0) + collected)
        resource_tile.storage = Resources(
            food=resource_tile.storage.food - (collected if resource_tile.acronym == "F" else 0),
            gold=resource_tile.storage.gold - (collected if resource_tile.acronym == "G" else 0),
            wood=resource_tile.storage.wood - (collected if resource_tile.acronym == "W" else 0),
        )
        if resource_tile.storage.food <= 0 and resource_tile.storage.gold <= 0 and resource_tile.storage.wood <= 0:
            game_map.remove_entity(resource_tile, resource_tile.x, resource_tile.y)
        self.task = False

    def stockResources(self, building, game_map, team):
        if not self.isAvailable() or not hasattr(building, 'resourceDropPoint') or not building.resourceDropPoint:
            return
        self.task = 'stock'
        self.move(building.x, building.y, game_map)
        team.resources = Resources(
            food=team.resources.food + self.resources.food,
            gold=team.resources.gold + self.resources.gold,
            wood=team.resources.wood + self.resources.wood,
        )
        self.resources = Resources(food=0, gold=0, wood=0)
        self.task = False

    def build(self, map,building):
        if not self.isAvailable():
            return
        self.task = 'build'
        self.move((building.x, building.y), map)
        building.constructors.append(self)

    
   
    '''