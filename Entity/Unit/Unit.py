import math
import pygame
from Entity.Entity import Entity
from Entity.Building import Building
from Settings.setup import FRAMES_PER_UNIT, HALF_TILE_SIZE, ALLOWED_ANGLES
from Controller.isometric_utils import tile_to_screen
from Controller.init_assets import draw_sprite

class Unit(Entity):
    id = 0
    # Increase the "fudge factor" => diagonal is about sqrt(2) ~1.41 => let's do 0.5
    ATTACK_RANGE_EPSILON = 0.5

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

    @staticmethod
    def compute_distance(pos1, pos2):
        return math.dist(pos1, pos2)

    def distance_to_target(self, game_map):
        """
        If target is building => gather building tiles => min distance
        Otherwise => distance to target.x,y
        """
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
        """
        If in range => do damage, else => approach
        On passe ici également le dt pour que si l'unité doit se déplacer,
        ce soit cohérent avec sa vitesse. 
        """
        if not self.target or self.target.hp <= 0:
            self.target = None
            return
        if self.target.team == self.team:
            return

        dist = self.distance_to_target(game_map)
        if dist is None:
            self.target = None
            return

        effective_range = self.attack_range + self.ATTACK_RANGE_EPSILON
        if dist <= effective_range:
            self.state = 2
            self.target.hp -= self.attack_power
            if hasattr(self.target, "notify_damage"):
                self.target.notify_damage()
        else:
            self.state = 1
            self.move_towards_target(game_map, dt)

    def move_towards_target(self, game_map, dt):
        """
        Attack-based movement => recalc path if we have none
        Au lieu de forcer dt=0.016, on récupère ici le dt réel, 
        afin que la vitesse respecte self.speed et le temps écoulé.
        """
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

        # On déplace d'après le dt réel
        self.do_move_step(game_map, dt)

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

    def distance_to_any_tile(self, upos, tile_list):
        if not tile_list:
            return None
        best = float('inf')
        for (tx, ty) in tile_list:
            d = math.dist(upos, (tx, ty))
            if d < best:
                best = d
        return best if best < float('inf') else None

    def find_best_adjacent_spot_to_building(self, building, game_map):
        btiles = self.get_building_tiles(building, game_map)
        if not btiles:
            return (round(building.x), round(building.y))

        neighbors = []
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for (bx, by) in btiles:
            for dx, dy in directions:
                nx, ny = bx + dx, by + dy
                if 0 <= nx < game_map.num_tiles_x and 0 <= ny < game_map.num_tiles_y:
                    if self.is_tile_walkable(game_map, nx, ny):
                        neighbors.append((nx, ny))

        if not neighbors:
            return (round(building.x), round(building.y))

        best = None
        best_sq = float('inf')
        for (cx, cy) in neighbors:
            dsq = (self.x - cx)**2 + (self.y - cy)**2
            if dsq < best_sq:
                best_sq = dsq
                best = (cx, cy)
        return best

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
