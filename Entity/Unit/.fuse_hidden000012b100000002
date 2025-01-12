import math
import pygame
from Settings.setup import MAXIMUM_CARRY, RESOURCE_RATE_PER_SEC, Resources, FRAMES_PER_UNIT, HALF_TILE_SIZE,TILE_SIZE, ALLOWED_ANGLES, ATTACK_RANGE_EPSILON, UNIT_HITBOX, villager_tasks
from Entity.Unit.Unit import Unit
from AiUtils.aStar import a_star
from Controller.utils import get_direction, get_snapped_angle

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
            attack_range=1, 
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
        if self.isAlive():
            self.setIdle()
            self.seekAttack(game_map, dt)
            self.seekCollision(game_map, dt)
            self.seekCollect(game_map, dt)
            self.seekStock(game_map)
            self.seekMove(game_map, dt)
            #self.seekBuild(game_map, dt)
        else:
            self.death(game_map, dt)

    # ---------------- Controller ----------------
    def set_target(self, target):
        self.attack_target = None
        self.collect_target = None
        self.build_target = None
        self.stock_target = None
        self.set_destination(None, None)

        if target and target.isAlive() and target.entity_id != self.entity_id:
            if target.hasResources:
                self.set_task('collect', target)

            elif target.team == self.team and hasattr(target, 'population'):
                if target.resourceDropPoint and target.state == 'idle':
                    self.set_task('stock', target)
                else:
                    self.set_task('build', target)
            
            elif target.team != self.team:
                self.attack_target = target

    def set_task(self, task, target = None):
        self.attack_target = None
        self.collect_target = None
        self.build_target = None
        self.stock_target = None
        self.task = None
        
        if task in villager_tasks:
            self.task = task
            setattr(self, villager_tasks[task], target)

    def isAvailable(self):
        return not self.task

    def seekCollect(self, game_map, dt):
        if self.task != 'collect':
            return

        if self.collect_target and self.collect_target.isAlive():
            distance = math.dist((self.x, self.y), (self.collect_target.x, self.collect_target.y)) - self.collect_target.hitbox - self.attack_range

            if distance <= 0 and self.carry.total() < MAXIMUM_CARRY :
                self.state = 'task'
                self.direction = get_direction(get_snapped_angle((self.x, self.y), (self.collect_target.x, self.collect_target.y)))
                if self.task_timer == 0 :
                    self.current_frame = 0
                    self.set_destination(None, game_map)
                self.task_timer += dt
                amount = min(self.resource_rate * dt, abs(MAXIMUM_CARRY - self.carry.total()))
                resource_collected = self.collect_target.storage.decrease_resources((amount, amount, amount))
                hp_damage = amount*self.collect_target.max_hp / self.collect_target.maximum_storage.total()
                self.collect_target.hp -= hp_damage
                self.carry.increase_resources(resource_collected)
                if self.carry.total() >= MAXIMUM_CARRY or not self.collect_target.isAlive():
                    self.task = 'stock'

            elif not self.path:
                self.set_destination((self.collect_target.x, self.collect_target.y), game_map)
                self.task_timer = 0

    def seekStock(self, game_map):
        if self.task != 'stock':
            return
        if self.stock_target and self.stock_target.isAlive():
            distance = math.dist((self.x, self.y), (self.stock_target.x, self.stock_target.y)) - self.stock_target.hitbox - self.attack_range
            if self.carry.total() == 0:
                    self.task = 'collect'
                    return
            if distance <= 0:
                self.state = 'idle'
                self.set_destination(None, game_map)
                self.carry.decrease_resources(self.stock_target.stock(game_map, self.carry.get()))
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

    
    def buildTime(self, building, num_villagers):
        return max(10, (3 * building.buildTime) / (num_villagers + 2)) if num_villagers > 0 else building.buildTime
    '''