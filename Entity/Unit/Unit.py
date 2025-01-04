import math
import pygame
from AiUtils.aStar import a_star
from Entity.Entity import Entity
from Entity.Building import Building
from Settings.setup import FRAMES_PER_UNIT, HALF_TILE_SIZE, ALLOWED_ANGLES, ATTACK_RANGE_EPSILON, UNIT_HITBOX
from Controller.isometric_utils import tile_to_screen, get_direction, get_snapped_angle
from Controller.init_assets import draw_sprite, draw_hitbox

class Unit(Entity):
    def __init__(
        self,
        x,
        y,
        team,
        acronym,
        max_hp,
        cost,
        attack_power,
        attack_range,
        attack_speed,
        speed,
        training_time
        ):
        super().__init__(x=x, y=y, team=team, acronym=acronym, size=1, max_hp=max_hp, cost=cost, walkable=True)
        
        self.attack_power = attack_power
        self.attack_range = attack_range
        self.attack_speed = attack_speed
        self.attack_timer = 0
        self.target = None
        self.attack_range_epsilon = ATTACK_RANGE_EPSILON
        
        self.speed = speed
        self.training_time = training_time
        self.path = None

        self.state = 0
        self.frames = FRAMES_PER_UNIT
        self.current_frame = 0
        self.frame_duration = 0
        self.direction = 0
        self.cooldown_frame = None

    # ---------------- Idle ----------------
    def setIdle(self):
        if self.state !=0:
            self.state = 0
        self.cooldown_frame = None

    # ---------------- Move Logic ----------------
    def move(self, game_map, dt, ALLOWED_ANGLES=ALLOWED_ANGLES):
        if not self.path:
            return
        self.state = 1
        target_tile = self.path[0]
        snapped_angle = get_snapped_angle((self.x, self.y), (target_tile[0], target_tile[1]))
        self.direction = get_direction(snapped_angle)
        step = ( dt *  self.speed * math.cos(math.radians(snapped_angle)), dt * self.speed * math.sin(math.radians(snapped_angle)))
        self.x += step[0]
        self.y += step[1]
        
        distance = math.dist((self.x, self.y), (target_tile[0], target_tile[1]))
        if distance < abs(step[0]) or distance < abs(step[1]):
            self.path.pop(0)
            game_map.remove_entity(self)
            game_map.add_entity(self, self.x, self.y)
        return self.path

    # ---------------- Attack Logic ----------------
    def set_target(self, target):
        if target:
            self.target = target
            print(f'set target : {target.x}, {target.y}')

    def attack(self, game_map, dt):
        if not self.target or not self.target.isAlive() or self.target.entity_id == self.entity_id or self.target.team == self.team:
            self.target = None

        else :
            distance = math.dist((self.x, self.y), (self.target.x, self.target.y))
            if distance < self.attack_range:
                self.state = 2
                self.direction = get_direction(get_snapped_angle((self.x, self.y), (self.target.x, self.target.y))) 

                if self.attack_timer == 0:
                    self.current_frame = 0
                    self.path = None
                
                elif self.current_frame == self.frames - 1:
                    self.cooldown_frame = self.current_frame
                    
                self.attack_timer += dt
                if self.attack_timer >= self.attack_speed:
                    self.target.hp -= self.attack_power
                    self.attack_timer = 0
                    self.cooldown_frame = None
            else:
                a_star(self, (round(self.target.x), round(self.target.y)), game_map)
                self.state = 1
                self.attack_timer = 0

    # ---------------- Death Logic ----------------
    def kill(self, game_map):
        self.state = 3
        self.cooldown_frame = None
        self.target = None
        self.path = None
        self.current_frame = 0
        self.hp = 0

        game_map.move_to_inactive(self)
        game_map.players[self.team].units.remove(self)

    def death(self, game_map):
        if self.current_frame == self.frames - 1 and self.state == 4:
            game_map.remove_inactive(self)

        if self.current_frame == self.frames - 1:
            self.state = 4
            self.current_frame = 0 


    # -------------- Display --------------
    def display(self, screen, screen_width, screen_height, camera, dt):
        self.frame_duration += dt
        frame_time = 1.0 / self.frames
        if self.frame_duration >= frame_time:
            self.frame_duration -= frame_time
            self.current_frame = (self.current_frame + 1) % self.frames

        if self.cooldown_frame:
            self.current_frame = self.cooldown_frame
        sx, sy = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, 'units', sx, sy, camera.zoom, state=self.state, frame=self.current_frame, direction=self.direction)

    def display_hitbox(self, screen, screen_width, screen_height, camera):
        x_center, y_center = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)

        corner_distance = UNIT_HITBOX
        
        corners = [
            (self.x - corner_distance, self.y - corner_distance),  # corner3
            (self.x - corner_distance, self.y + corner_distance),  # corner1
            (self.x + corner_distance, self.y + corner_distance),  # corner2
            (self.x + corner_distance, self.y - corner_distance)   # corner4
        ]
        
        screen_corners = []
        for corner in corners:
            x_screen, y_screen = tile_to_screen(corner[0], corner[1], HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
            screen_corners.append((x_screen, y_screen))
        
        draw_hitbox(screen, screen_corners, camera.zoom)