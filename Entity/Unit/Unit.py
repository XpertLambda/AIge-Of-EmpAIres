import math
from Entity.Entity import Entity
from Settings.setup import FRAMES_PER_UNIT, HALF_TILE_SIZE
from Controller.isometric_utils import tile_to_screen, angle_with_x_axis
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

        self.last_step_time = pygame.time.get_ticks()
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

    def move(self, time, target_pos, game_map):
        if time - self.last_step_time > UPDATE_EVERY_N_MILLISECOND :
            self.last_step_time = current_time
            dx = target_pos[0] - self.x
            dy = target_pos[1] - self.y
            angle = angle_with_x_axis(dx,dy)
            self.x = self.x + math.cos(angle)*(self.speed*TILE_SIZE*UPDATE_EVERY_N_MILLISECOND / ONE_SECOND)
            self.y = self.y + math.sin(angle)*(self.speed*TILE_SIZE*UPDATE_EVERY_N_MILLISECOND / ONE_SECOND)
            if dx > TILE_SIZE or dy > TILE_SIZE : 
                game_map.remove_entity(game_map.grid, round(self.x), round(self.y), self)
                game_map.add_entity(game_map.grid, round(self.x), round(self.y), self)

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

# game_loop used to test the A* algorithm

# import time
# import pygame
# import sys
# import random
# from Controller.camera import Camera
# from Controller.drawing import (
#     draw_map,
#     compute_map_bounds,
#     create_minimap_background,
#     display_fps,
#     update_minimap_entities,
#     draw_minimap_viewport,
#     generate_team_colors
# )
# from Controller.event_handler import handle_events
# from Controller.update import update_game_state
# from Controller.select_player import create_player_selection_surface, create_player_info_surface
# from Settings.setup import MINIMAP_MARGIN, HALF_TILE_SIZE
# from Controller.isometric_utils import tile_to_screen  # Import the tile_to_screen function

# from Entity.Unit import Unit

# def game_loop(screen, game_map, screen_width, screen_height, players):
#     clock = pygame.time.Clock()
#     camera = Camera(screen_width, screen_height)
#     team_colors = generate_team_colors(len(players))
#     min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_map)
#     camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)

#     minimap_margin = MINIMAP_MARGIN
#     minimap_width = int(screen_width * 0.25)
#     minimap_height = int(screen_height * 0.25)
#     minimap_rect = pygame.Rect(
#         screen_width - minimap_width - minimap_margin,
#         screen_height - minimap_height - minimap_margin,
#         minimap_width,
#         minimap_height
#     )

#     minimap_background, minimap_scale, minimap_offset_x, minimap_offset_y, \
#     minimap_min_iso_x, minimap_min_iso_y = create_minimap_background(
#         game_map, minimap_width, minimap_height
#     )

#     minimap_entities_surface = pygame.Surface((minimap_width, minimap_height), pygame.SRCALPHA)
#     minimap_entities_surface.fill((0, 0, 0, 0))

#     selected_player = players[0] if players else None
#     minimap_dragging = False
#     fullscreen = False

#     game_state = {
#         'camera': camera,
#         'players': players,
#         'selected_player': selected_player,
#         'minimap_rect': minimap_rect,
#         'minimap_dragging': minimap_dragging,
#         'minimap_background': minimap_background,
#         'minimap_scale': minimap_scale,
#         'minimap_offset_x': minimap_offset_x,
#         'minimap_offset_y': minimap_offset_y,
#         'minimap_min_iso_x': minimap_min_iso_x,
#         'minimap_min_iso_y': minimap_min_iso_y,
#         'game_map': game_map,
#         'screen_width': screen_width,
#         'screen_height': screen_height,
#         'minimap_margin': minimap_margin,
#         'screen': screen,
#         'fullscreen': fullscreen,
#         'player_selection_updated': True,
#         'player_info_updated': True,
#         'minimap_entities_surface': minimap_entities_surface,
#         'team_colors': team_colors,
#         'selecting_units': False,
#         'selection_start': None,
#         'selection_end': None,
#         'selected_units': [],
#         'show_all_health_bars': False
#     }

#     player_selection_surface = None
#     player_info_surface = None

#     # Initialize A* pathfinding for a test unit
#     test_unit = players[0].units[0]  # Assume the first player's first unit
#     start_pos = (test_unit.x, test_unit.y)
#     goal_pos = (10, 10)  # Example goal position
#     path = Unit.a_star(test_unit, start_pos, goal_pos, game_map)
#     move_speed = 10  # Updated move speed to 10 units at a time

#     if path:
#         print(f"Path found: {path}")
#     else:
#         print("No path found.")
#         path = []

#     running = True
#     update_interval = 60
#     frame_counter = 0

#     while running:
#         dt = clock.tick(120) / 1000
#         frame_counter += 1

#         for event in pygame.event.get():
#             handle_events(event, game_state)
#             if event.type == pygame.QUIT:
#                 running = False

#         if path:
#             path = Unit.move_unit(test_unit, path, game_map, move_speed, dt)

#             # Debugging unit position
#             print(f"Unit position: {test_unit.x}, {test_unit.y}")

#         update_game_state(game_state, dt)

#         camera = game_state['camera']
#         minimap_rect = game_state['minimap_rect']
#         screen = game_state['screen']
#         screen_width = game_state['screen_width']
#         screen_height = game_state['screen_height']
#         selected_player = game_state['selected_player']
#         players = game_state['players']
#         team_colors = game_state['team_colors']
#         game_map = game_state['game_map']

#         if game_state.get('recompute_camera', False):
#             min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_map)
#             camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)
#             game_state['recompute_camera'] = False

#         if not game_state.get('paused', False):
#             if frame_counter % update_interval == 0:
#                 update_minimap_entities(game_state)

#             if game_state.get('player_selection_updated', False):
#                 player_selection_surface = create_player_selection_surface(
#                     players, selected_player, minimap_rect, team_colors)
#                 game_state['player_selection_updated'] = False

#             if game_state.get('player_info_updated', False):
#                 player_info_surface = create_player_info_surface(
#                     selected_player, screen_width, team_colors)
#                 game_state['player_info_updated'] = False

#         screen.fill((0, 0, 0))
#         draw_map(screen, screen_width, screen_height, game_map, camera, players, team_colors, game_state)

#         screen.blit(game_state['minimap_background'], minimap_rect.topleft)
#         screen.blit(game_state['minimap_entities_surface'], minimap_rect.topleft)
#         draw_minimap_viewport(screen, camera, minimap_rect,
#                               game_state['minimap_scale'],
#                               game_state['minimap_offset_x'],
#                               game_state['minimap_offset_y'],
#                               game_state['minimap_min_iso_x'],
#                               game_state['minimap_min_iso_y'])

#         if player_selection_surface:
#             sel_h = player_selection_surface.get_height()
#             screen.blit(player_selection_surface, (minimap_rect.x, minimap_rect.y - sel_h))

#         if player_info_surface:
#             inf_h = player_info_surface.get_height()
#             screen.blit(player_info_surface, (0, screen_height - inf_h))

#         display_fps(screen, clock)
#         pygame.display.flip()
pass