import math
import pygame
from Entity.Entity import Entity
from Entity.Building import Building
from Settings.setup import FRAMES_PER_UNIT, HALF_TILE_SIZE, ALLOWED_ANGLES, ATTACK_RANGE_EPSILON
from Controller.isometric_utils import tile_to_screen
from Controller.init_assets import draw_sprite

class Unit(Entity):
    id = 0


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
        speed,
        training_time
    ):
        super().__init__(x, y, team, acronym, 1, max_hp, cost)
        self.attack_power = attack_power
        self.attack_range = attack_range
        self.speed = speed
        self.training_time = training_time

        self.unit_id = Unit.id
        Unit.id += 1

        self.path = None
        self.state = 0  # 0=idle,1=walk,2=attack
        self.last_frame_time = pygame.time.get_ticks()
        self.frames = FRAMES_PER_UNIT
        self.current_frame = 0
        self.frame_duration = 1000 / self.frames
        self.direction = 0

        self.target = None
        self.attack_range_epsilon = ATTACK_RANGE_EPSILON

    @staticmethod
    def compute_distance(pos1, pos2):
        return math.dist(pos1, pos2)

    def distance_to_target(self, game_map):
        if not self.target:
            return None
        if isinstance(self.target, Building):
            tiles = self.get_building_tiles(self.target, game_map)
            return self.distance_to_any_tile((self.x, self.y), tiles)
        else:
            return self.compute_distance((self.x, self.y),
                                         (self.target.x, self.target.y))

    def move(self, game_map, dt, ALLOWED_ANGLES=ALLOWED_ANGLES):
        if not self.path:
            self.state = 0
            return

        self.state = 1
        target_tile = self.path[0]
        dx = target_tile[0] - self.x
        dy = target_tile[1] - self.y
        angle = math.degrees(math.atan2(dy, dx))
        angle = (angle + 360) % 360
        snapped_angle = min(ALLOWED_ANGLES, key=lambda x: abs(x - angle))
        snapped_angle_rad = math.radians(snapped_angle)
        step = ( dt *  self.speed * math.cos(snapped_angle_rad), dt * self.speed * math.sin(snapped_angle_rad))
        self.x += step[0]
        self.y += step[1]
        if abs(dx) < abs(step[0]) or abs(dy) < abs(step[1]):
            self.path.pop(0)
            game_map.remove_entity(self, self.x, self.y)
            game_map.add_entity(self, self.x, self.y)
        self.direction = ((snapped_angle // 45 )+1)%8 # +1 to match the sprite sheet and %8 because tere are 8 directions
        return self.path

    # ---------------- Attack Logic ----------------
    def attack(self, attacker_team, game_map, dt):

        if not self.target or self.target.hp <= 0:
            self.target = None
            return
        if self.target.team == self.team:
            return

        distance = self.distance_to_target(game_map)
        if distance is None:
            self.target = None
            return

        effective_range = self.attack_range + self.attack_range_epsilon
        if distance <= effective_range:
            self.state = 2
            self.target.hp -= self.attack_power
            if hasattr(self.target, "notify_damage"):
                self.target.notify_damage()
        else:
            self.state = 1
            self.move_towards_target(game_map, dt)

    def move_towards_target(self, game_map, dt):
        if not self.target:
            return

        if isinstance(self.target, Building):
            near_tile = self.find_best_adjacent_spot_to_building(self.target, game_map)
            if not self.path:
                from AiUtils.aStar import a_star
                a_star(self, near_tile, game_map)
        else:
            # unit
            if not self.path:
                from AiUtils.aStar import a_star
                a_star(self, (round(self.target.x), round(self.target.y)), game_map)

        if not self.path:
            self.state = 0
            return

    # ---------------- Building Distances ----------------
    def get_building_tiles(self, building, game_map):
        tiles = []
        x_min = max(0, round(building.x) - building.size)
        x_max = min(game_map.num_tiles_x, round(building.x) + building.size)
        y_min = max(0, round(building.y) - building.size)
        y_max = min(game_map.num_tiles_y, round(building.y) + building.size)
        for xx in range(x_min, x_max + 1):
            for yy in range(y_min, y_max + 1):
                entset = game_map.grid.get((xx, yy), None)
                if entset and building in entset:
                    tiles.append((xx, yy))
        return tiles

    def distance_to_any_tile(self, unit_position, tile_list):
        if not tile_list:
            return None
        best_distance = float('inf')
        for (tile_x, tile_y) in tile_list:
            distance = math.dist(unit_position, (tile_x, tile_y))
            if distance < best_distance:
                best_distance = distance
        return best_distance if best_distance < float('inf') else None

    def find_best_adjacent_spot_to_building(self, building, game_map):
        # Direction from building center to the unit
        dx = self.x - building.x
        dy = self.y - building.y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance < 1e-7:
            return (round(building.x), round(building.y))

        # Near edge offset
        offset = building.size / 2.0 + 0.5
        if distance <= offset:
            # Fallback if the unit is already too close
            return (round(building.x), round(building.y))

        # Find the point near the edge closest to the unit
        ratio = offset / distance
        near_x = building.x + ratio * dx
        near_y = building.y + ratio * dy
        tile_x, tile_y = round(near_x), round(near_y)

        # Check if walkable
        if self.is_tile_walkable(game_map, tile_x, tile_y):
            return (tile_x, tile_y)

        # Optional: check surrounding tiles or simply fallback
        return (round(building.x), round(building.y))

    # ---------------- Map Walkability ----------------
    def is_tile_walkable(self, game_map, tx, ty):
        if tx < 0 or ty < 0 or tx >= game_map.num_tiles_x or ty >= game_map.num_tiles_y:
            return False
        entset = game_map.grid.get((tx, ty), None)
        if entset:
            for e in entset:
                if hasattr(e, 'walkable') and not e.walkable:
                    return False
        return True

    # -------------- Display --------------
    def display(self, screen, screen_width, screen_height, camera):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_time > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % self.frames + self.frames * self.direction
            self.last_frame_time = current_time

        sx, sy = tile_to_screen(self.x, self.y,HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, 'units', sx, sy, camera.zoom, state=self.state, frame=self.current_frame)
