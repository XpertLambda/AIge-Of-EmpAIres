import math
import pygame
from Entity.Entity import Entity
from Settings.setup import FRAMES_PER_UNIT, TILE_SIZE, HALF_TILE_SIZE, UPDATE_EVERY_N_MILLISECOND, ONE_SECOND, ALLOWED_ANGLES
from Controller.isometric_utils import tile_to_screen, angle_with_x_axis
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
        super().__init__(x=x, y=y, team=team, acronym=acronym, size=1, max_hp=max_hp, cost=cost)
        self.attack_power = attack_power
        self.attack_range = attack_range
        self.speed = speed
        self.training_time = training_time
        self.task=False
        self.unit_id = Unit.id

        # Movement
        self.path = None
        self.last_step_time = pygame.time.get_ticks()

        # State variables
        self.state = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.frames = FRAMES_PER_UNIT
        self.current_frame = 0
        self.frame_duration = 1000/self.frames
        self.direction = 0

        self.target = None
        Unit.id += 1

    @staticmethod
    def compute_distance(pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def attack(self, attacker_team, game_map):
        target_found = True

        if self.target is None or self.target.hp <= 0:
            target_found = self.search_for_target(attacker_team)

        if target_found and self.target is not None:
            distance_to_target = self.compute_distance((self.x, self.y), (self.target.x, self.target.y))
            if distance_to_target < 100:
                # Perform the attack
                self.current_frame = 0
                self.target.hp -= self.attack_power
                if hasattr(self.target, "notify_damage"):
                    self.target.notify_damage()
            else:
                # Move closer to the target
                # We'll pass 0 dt if paused => no movement
                self.move(game_map, 0.016)  # example dt if we want forced step
        return target_found

    def search_for_target(self, enemy_team, attack_mode=True):
        """
        Searches for the closest enemy unit or building depending on the mode.
        """
        closest_distance = float("inf")
        closest_entity = None

        # Suppose enemy_team has a list of units in "army" or "units"
        # This example code might differ from your production code
        if hasattr(enemy_team, 'army'):
            enemy_units_list = enemy_team.army
        else:
            enemy_units_list = enemy_team.units

        for enemy_unit in enemy_units_list:
            dist = self.compute_distance((self.x, self.y), (enemy_unit.x, enemy_unit.y))
            if attack_mode or dist < 100:
                if dist < closest_distance:
                    closest_distance = dist
                    closest_entity = enemy_unit

        if attack_mode and hasattr(enemy_team, 'buildings'):
            for enemy_building in enemy_team.buildings:
                dist = self.compute_distance((self.x, self.y), (enemy_building.x, enemy_building.y))
                if dist < closest_distance:
                    closest_distance = dist
                    closest_entity = enemy_building

        self.target = closest_entity
        return self.target is not None

    def is_tile_walkable(self, game_map, tile_x, tile_y):
        if (
            tile_x < 0 or
            tile_y < 0 or
            tile_x >= game_map.num_tiles_x or
            tile_y >= game_map.num_tiles_y
        ):
            return False

        tile_pos = (tile_x, tile_y)
        entities_on_tile = game_map.grid.get(tile_pos, None)

        if entities_on_tile:
            for entity in entities_on_tile:
                # For example, if that tile is occupied by a non-walkable building
                if hasattr(entity, "walkable") and not entity.walkable:
                    return False
        return True

    def move(self, game_map, dt, ALLOWED_ANGLES=ALLOWED_ANGLES):
        """
        Move with dt-based increments. If dt <= 0 => skip to avoid
        accumulation or 'jump' after unpause.
        """
        if not self.path or dt <= 0:
            self.state = 0
            self.last_step_time = pygame.time.get_ticks()
            return

        self.state = 1
        # Time since last step
        ms_since_last = pygame.time.get_ticks() - self.last_step_time
        # If enough ms have passed => do a step
        if ms_since_last > UPDATE_EVERY_N_MILLISECOND:
            self.last_step_time = pygame.time.get_ticks()

            # Target tile is self.path[0]
            target_tile = self.path[0]
            dx = target_tile[0] - self.x
            dy = target_tile[1] - self.y
            angle = math.degrees(math.atan2(dy, dx))
            angle = (angle + 360) % 360
            snapped_angle = min(ALLOWED_ANGLES, key=lambda x: abs(x - angle))
            snapped_angle_rad = math.radians(snapped_angle)

            # distance per second => use dt
            step_x = (dt * self.speed) * math.cos(snapped_angle_rad)
            step_y = (dt * self.speed) * math.sin(snapped_angle_rad)

            self.x += step_x
            self.y += step_y

            # If we've passed or reached the target tile => remove it from path
            # We check if the new step is overshooting
            if (abs(dx) < abs(step_x)) or (abs(dy) < abs(step_y)):
                # Remove the tile from path
                self.path.pop(0)
                # Update game_map to reflect new position
                game_map.remove_entity(self, self.x, self.y)
                game_map.add_entity(self, self.x, self.y)

            # Direction for sprite
            # e.g. snapped_angle // 45 => direction in [0..7]
            self.direction = int((snapped_angle // 45) % 8)

    def display(self, screen, screen_width, screen_height, camera):
        dt = pygame.time.get_ticks() - self.last_frame_time
        if dt > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % self.frames + self.frames*self.direction
            self.last_frame_time = pygame.time.get_ticks()

        screen_x, screen_y = tile_to_screen(
            self.x,
            self.y,
            HALF_TILE_SIZE,
            HALF_TILE_SIZE / 2,
            camera,
            screen_width,
            screen_height
        )

        # Draw the unit sprite
        draw_sprite(
            screen,
            self.acronym,
            category='units',
            screen_x=screen_x,
            screen_y=screen_y,
            zoom=camera.zoom,
            state=self.state,
            frame=self.current_frame
        )
