import math
from Entity.Entity import Entity
from Settings.setup import FRAMES_PER_UNIT, HALF_TILE_SIZE
from Controller.isometric_utils import tile_to_screen
from Controller.init_sprites import draw_sprite
import heapq
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

        self.unit_id = Unit.id
        Unit.id += 1
        self.task=False
        # State variables
        self.state = 0
        self.frames = FRAMES_PER_UNIT
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_duration = 3
        self.direction = 0

        self.target = None

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
                self.frame_counter = 0
                self.target.hp -= self.attack_power
                # Notify or handle damage on target
                if hasattr(self.target, "notify_damage"):
                    self.target.notify_damage()
            else:
                # Move closer to the target
                self.move((self.target.x, self.target.y), game_map)

        return target_found

    def search_for_target(self, enemy_team, attack_mode=True):
        """
        Searches for the closest enemy unit or building depending on the mode.
        """
        closest_distance = float("inf")
        closest_entity = None

        for enemy_unit in enemy_team.army:
            dist = self.compute_distance((self.x, self.y), (enemy_unit.x, enemy_unit.y))
            if attack_mode or dist < 100: 
                if dist < closest_distance:
                    closest_distance = dist
                    closest_entity = enemy_unit

        if attack_mode:
            for enemy_building in enemy_team.buildings:
                dist = self.compute_distance((self.x, self.y), (enemy_building.x, enemy_building.y))
                if dist < closest_distance:
                    closest_distance = dist
                    closest_entity = enemy_building

        self.target = closest_entity
        return self.target is not None

    def is_tile_walkable(self, game_map, tile_x, tile_y):
        """
        Checks if a tile at (tile_x, tile_y) is walkable for this unit.
        """
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
                # Example check for building walkability
                if hasattr(entity, "walkable") and not entity.walkable:
                    return False

        return True

    def move(self, target_pos, game_map):
        """
        Tries to step closer to the target position (target_pos) by checking tile walkability.
        Adjusts the direction based on movement.
        """
        self.frame_counter = 0
        self.current_frame = 0

        target_x = int(target_pos[0])
        target_y = int(target_pos[1])

        dx = 0
        dy = 0
        if self.x < target_x:
            dx = 1
        elif self.x > target_x:
            dx = -1

        if self.y < target_y:
            dy = 1
        elif self.y > target_y:
            dy = -1

        # Attempt diagonal movement if possible
        if dx != 0 and dy != 0:
            new_x = self.x + dx
            new_y = self.y + dy
            if self.is_tile_walkable(game_map, int(new_x), int(new_y)):
                self.x = new_x
                self.y = new_y
                # Set direction based on dx/dy
                if dx == 1 and dy == 1:
                    self.direction = 270
                elif dx == 1 and dy == -1:
                    self.direction = 90
                elif dx == -1 and dy == 1:
                    self.direction = 225
                elif dx == -1 and dy == -1:
                    self.direction = 45
                return

        # Attempt horizontal movement
        if dx != 0:
            new_x = self.x + dx
            if self.is_tile_walkable(game_map, int(new_x), int(self.y)):
                self.x = new_x
                self.direction = 135 if dx == 1 else 315
                return

        # Attempt vertical movement
        if dy != 0:
            new_y = self.y + dy
            if self.is_tile_walkable(game_map, int(self.x), int(new_y)):
                self.y = new_y
                self.direction = 225 if dy == 1 else 45

    def display(self, screen, screen_width, screen_height, camera):
        """
        Displays the unit on the screen with sprite animations.
        """
        # Update frame handling for animation
        self.frame_counter += 1
        if self.frame_counter >= self.frame_duration:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % self.frames

        # Convert tile coordinates to screen coordinates
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
        
    def a_star(unit, start, goal, game_map):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
        def get_neighbors(position):
            directions = [
                (1, 0), (0, 1), (-1, 0), (0, -1),
                (1, 1), (1, -1), (-1, 1), (-1, -1)
            ]
            neighbors = []
            for dx, dy in directions:
                neighbor = (position[0] + dx, position[1] + dy)
                if unit.is_tile_walkable(game_map, neighbor[0], neighbor[1]):
                    neighbors.append(neighbor)
            return neighbors
    
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
    
        while open_set:
            _, current = heapq.heappop(open_set)
        
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
        
            for neighbor in get_neighbors(current):
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
        return []
    def move_unit(unit, path, game_map, move_speed, dt):
        if not path:
            return None

        current_position = (unit.x, unit.y)
        target_position = path[0]

        direction_x = target_position[0] - current_position[0]
        direction_y = target_position[1] - current_position[1]
        distance = (direction_x**2 + direction_y**2) ** 0.5

        step_x = direction_x / distance * move_speed * dt if distance != 0 else 0
        step_y = direction_y / distance * move_speed * dt if distance != 0 else 0

        new_x = unit.x + step_x
        new_y = unit.y + step_y

        if abs(new_x - target_position[0]) < 0.1 and abs(new_y - target_position[1]) < 0.1:
            game_map.remove_entity(game_map.grid, int(unit.x), int(unit.y), unit)
            unit.x, unit.y = target_position
            game_map.add_entity(game_map.grid, int(unit.x), int(unit.y), unit)
            path.pop(0)
        else:
            game_map.remove_entity(game_map.grid, int(unit.x), int(unit.y), unit)
            unit.x, unit.y = new_x, new_y
            game_map.add_entity(game_map.grid, int(unit.x), int(unit.y), unit)

        return path
