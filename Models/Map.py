import math
import random
import os
import pickle
import time
import shutil
from collections import Counter
from datetime import datetime
from Entity.Building import *
from Entity.Unit import *
from Entity.Resource.Resource import *
from Entity.Resource.Gold import Gold
from Entity.Resource.Tree import Tree
from Settings.setup import BUILDING_ZONE_OFFSET, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, NUM_GOLD_TILES, NUM_WOOD_TILES, NUM_FOOD_TILES, GOLD_SPAWN_MIDDLE, SAVE_DIRECTORY
from Controller.terminal_display_debug import debug_print

class GameMap:
    def __init__(self, grid_width, grid_height, center_gold_flag, players, generate=True):
        self.grid_size = (grid_width, grid_height)  # Optionally store as tuple if needed
        self.num_tiles_x = grid_width
        self.num_tiles_y = grid_height
        self.center_gold_flag = center_gold_flag
        self.players = players
        self.num_tiles = self.num_tiles_x * self.num_tiles_y
        self.grid = {}
        self.resources = {}
        self.inactive_matrix = {}
        self.projectiles = {}
        self.game_state = None
        self.width = grid_width
        self.height = grid_height
        self.terminal_view_x = 0
        self.terminal_view_y = 0

        if generate:
            self.generate_map()
            
    def add_entity(self, entity, x, y):
        # Add safety check for team ID
        if hasattr(entity, 'team') and entity.team is not None:
            if entity.team >= len(self.players):
                print(f"Warning: Entity team ID {entity.team} out of range for {len(self.players)} players")
                return False

        rounded_x, rounded_y = round(x), round(y)
        if (rounded_x < 0 or rounded_y < 0
            or rounded_x + entity.size - 1 >= self.num_tiles_x
            or rounded_y + entity.size - 1 >= self.num_tiles_y):
            return False

        for i in range(entity.size):
            for j in range(entity.size):
                pos = (rounded_x + i, rounded_y + j)
                if pos in self.grid:
                    for existing_entity in self.grid[pos]:
                        if not self.walkable_position(pos):
                            return False

        for i in range(entity.size):
            for j in range(entity.size):
                pos = (rounded_x + i, rounded_y + j)
                if pos not in self.grid:
                    self.grid[pos] = set()
                self.grid[pos].add(entity)
                if entity.hasResources:
                    if pos not in self.resources:
                        self.resources[pos] = set()
                    self.resources[pos].add(entity)


        entity.x = x + (entity.size - 1) / 2
        entity.y = y + (entity.size - 1) / 2
        if entity.team != None:
            self.players[entity.team].add_member(entity)
            if isinstance(entity, Building):
                zone = self.players[entity.team].zone.add_zone((x - BUILDING_ZONE_OFFSET , y - BUILDING_ZONE_OFFSET), (x + entity.size - 1 + BUILDING_ZONE_OFFSET, y + entity.size - 1 + BUILDING_ZONE_OFFSET ))
        return True

    def remove_entity(self, entity):
        if not entity:
            return False
            
        remove_counter = 0
        for pos, matrix_entities in list(self.grid.items()):
            for matrix_entity in list(matrix_entities):
                if matrix_entity.entity_id == entity.entity_id:
                    matrix_entities.remove(matrix_entity)
                    remove_counter += 1
                    if not matrix_entities:
                        del self.grid[pos]
                    if remove_counter >= entity.size * entity.size:
                        if entity.team != None:
                            self.players[entity.team].remove_member(entity)
                            # Mise à jour de old_resources quand une entité est supprimée
                            if self.game_state and 'old_resources' in self.game_state:
                                if entity.team in self.game_state['old_resources']:
                                    self.game_state['old_resources'][entity.team] = self.players[entity.team].resources.copy()
                            
                            if isinstance(entity, Building):
                                x, y = entity.x , entity.y
                                starting_point = (x - entity.size/2 + 0.5  - BUILDING_ZONE_OFFSET, y - entity.size/2 + 0.5 - BUILDING_ZONE_OFFSET)
                                end_point = (x + entity.size/2 - 0.5  + BUILDING_ZONE_OFFSET , y + entity.size/2 - 0.5 + BUILDING_ZONE_OFFSET)
                                zone = self.players[entity.team].zone.remove_zone(starting_point, end_point)
                        return pos
        return False

    def walkable_position(self, position):
        x, y = round(position[0]), round(position[1])
        if x < 0 or y < 0 or x >= self.num_tiles_x or y >= self.num_tiles_y:
            return False

        entities = self.grid.get((x, y), None)
        if entities:
            for entity in entities:
                if not entity.walkable:
                    return False
        return True
    def buildable_position(self, x, y , size=1):
        rounded_x, rounded_y = round(x), round(y)
        if (rounded_x < 0 or rounded_y < 0
            or rounded_x + size - 1 >= self.num_tiles_x
            or rounded_y + size - 1 >= self.num_tiles_y):
            return False

        for i in range(size):
            for j in range(size):
                pos = (rounded_x + i, rounded_y + j)
                if pos in self.grid:
                    return False
        return True

    def generate_zones(self):
        cols = int(math.ceil(math.sqrt(len(self.players))))
        rows = int(math.ceil(len(self.players) / cols))
        zone_width = self.num_tiles_x // cols
        zone_height = self.num_tiles_y // rows

        for i, player in enumerate(self.players):
            row = i // cols
            col = i % cols
            x_start = col * zone_width
            y_start = row * zone_height
            x_end = min(x_start + zone_width, self.num_tiles_x)
            y_end = min(y_start + zone_height, self.num_tiles_y)
            player.zone.reset()
            player.zone.set_zone((x_start, y_start), (x_end - 1, y_end - 1))

    def generate_buildings(self):
        for player in self.players:
            zone_coords = list(player.zone.get_zone())
            if not zone_coords:
                continue
            x_vals = [x for x, _ in zone_coords]
            y_vals = [y for _, y in zone_coords]
            x_min, x_max = min(x_vals), max(x_vals)
            y_min, y_max = min(y_vals), max(y_vals)
            for building in player.buildings:
                max_attempts = (x_max - x_min + 1) * (y_max - y_min + 1)
                attempts = 0
                placed = False
                while attempts < max_attempts:
                    x = random.randint(x_min, max(x_min, x_max - building.size + 1))
                    y = random.randint(y_min, max(y_min, y_max - building.size + 1))
                    placed = self.add_entity(building, x, y)
                    if placed:
                        break
                    attempts += 1
                if not placed:
                    # fallback
                    for tile_y in range(self.num_tiles_y - building.size):
                        for tile_x in range(self.num_tiles_x - building.size):
                            placed = self.add_entity(building, tile_x, tile_y)
                            if placed:
                                break
                        if placed:
                            break
                    if not placed:
                        raise ValueError("Unable to deploy building (map too crowded?)")

    def generate_units(self):
        for player in self.players:
            zone_coords = list(player.zone.get_zone())
            if not zone_coords:
                continue
            x_vals = [x for x, _ in zone_coords]
            y_vals = [y for _, y in zone_coords]
            x_min, x_max = min(x_vals), max(x_vals)
            y_min, y_max = min(y_vals), max(y_vals)
            for unit in player.units:
                placed = False
                attempts = 0
                while not placed and attempts < 1000:
                    x_unit = random.randint(x_min, x_max)
                    y_unit = random.randint(y_min, y_max)
                    placed = self.add_entity(unit, x_unit, y_unit)
                    attempts += 1
                if not placed:
                    # fallback
                    attempts = 0
                    while not placed and attempts < 1000:
                        x_unit = random.randint(0, self.num_tiles_x - 1)
                        y_unit = random.randint(0, self.num_tiles_y - 1)
                        placed = self.add_entity(unit, x_unit, y_unit)
                        attempts += 1
                    if not placed:
                        debug_print(f"Warning: Failed to deploy unit for player {player.teamID} after multiple attempts.")

    def place_gold_near_town_centers(self):
        town_centers = [pos for pos, entities in self.grid.items() if any(isinstance(e, TownCentre) for e in entities)]
        for center in town_centers:
            x, y = center
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                dx = random.choice([-2, -1, 0, 1])
                dy = random.choice([-2, -1, 0, 1])
                if self.can_place_group(self.grid, x + dx, y + dy):
                    for i in range(2):
                        for j in range(2):
                            gold = Gold(x + dx + i, y + dy + j)
                            self.add_entity(gold, x + dx + i, y + dy + j)
                    placed = True
                attempts += 1

    def can_place_group(self, grid, x, y):
        if x + 1 < self.num_tiles_x and y + 1 < self.num_tiles_y:
            return all((x + dx, y + dy) not in grid for dx in range(2) for dy in range(2))
        return False

    def generate_map(self):
        self.generate_resources()
        self.place_gold_near_town_centers()

        self.generate_zones()
        self.generate_buildings()
        self.generate_units()
        return self.grid

    def generate_resources(self):
        resource_classes = {'gold': Gold, 'wood': Tree}
        if self.center_gold_flag:
            center_x = self.num_tiles_x // 2
            center_y = self.num_tiles_y // 2
            gold_count = 0
            layer = 0
            max_layer = max(self.num_tiles_x, self.num_tiles_y)
            while gold_count < NUM_GOLD_TILES and layer < max_layer:
                for dx in range(-layer, layer + 1):
                    for dy in range(-layer, layer + 1):
                        x = center_x + dx
                        y = center_y + dy
                        if 0 <= x < self.num_tiles_x and 0 <= y < self.num_tiles_y and (x, y) not in self.grid:
                            self.grid[(x, y)] = set()
                            self.grid[(x, y)].add(resource_classes['gold'](x, y))
                            gold_count += 1
                            if gold_count >= NUM_GOLD_TILES:
                                break
                    if gold_count >= NUM_GOLD_TILES:
                        break
                layer += 1
        else:
            gold_placed = 0
            while gold_placed < NUM_GOLD_TILES:
                x_start = random.randint(0, self.num_tiles_x - 2)
                y_start = random.randint(0, self.num_tiles_y - 2)
                for i in range(2):
                    for j in range(2):
                        if gold_placed >= NUM_GOLD_TILES:
                            break
                        x = x_start + i
                        y = y_start + j
                        attempts = 0
                        placed = False
                        while not placed and attempts < 10:
                            resource = resource_classes['gold'](x, y)
                            placed = self.add_entity(resource, x, y)
                            attempts += 1
                        if placed:
                            gold_placed += 1
                    if gold_placed >= NUM_GOLD_TILES:
                        break

        cluster_size_min, cluster_size_max = 2, 4
        wood_placed = 0
        while wood_placed < NUM_WOOD_TILES:
            cluster_size = random.randint(cluster_size_min, cluster_size_max)
            x_start = random.randint(0, self.num_tiles_x - cluster_size)
            y_start = random.randint(0, self.num_tiles_y - cluster_size)
            for i in range(cluster_size):
                for j in range(cluster_size):
                    if wood_placed >= NUM_WOOD_TILES:
                        break
                    x = x_start + i
                    y = y_start + j
                    attempts = 0
                    placed = False
                    while not placed and attempts < 10:
                        resource = resource_classes['wood'](x, y)
                        placed = self.add_entity(resource, x, y)
                        attempts += 1
                    if placed:
                        wood_placed += 1
                if wood_placed >= NUM_WOOD_TILES:
                    break

    def debug_print_map(self):
        """
        Affichage complet (debug)
        """
        for y in range(self.num_tiles_y):
            row_display = []
            for x in range(self.num_tiles_x):
                pos = (x, y)
                if pos in self.grid:
                    entities = self.grid[pos]
                    acr = list(entities)[0].acronym if entities else ' '
                    row_display.append(acr)
                else:
                    row_display.append(' ')
            debug_print(''.join(row_display))

    def save_map(self, filename=None):
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"save_{timestamp}.pkl"
        else:
            if not filename.endswith('.pkl'):
                filename += '.pkl'
        full_path = os.path.join(SAVE_DIRECTORY, filename)

        # Temporarily store and remove unpicklable objects
        gui_state = {}
        if self.game_state:
            # Store current bot modes before saving
            self.game_state['bot_modes'] = self.game_state.get('bot_modes', ['economique'] * len(self.players))
            
            gui_state = {
                'screen': self.game_state.pop('screen', None),
                'minimap_panel_sprite': self.game_state.pop('minimap_panel_sprite', None),
                'minimap_background': self.game_state.pop('minimap_background', None),
                'minimap_entities_surface': self.game_state.pop('minimap_entities_surface', None),
                'player_selection_surface': self.game_state.pop('player_selection_surface', None),
                'train_button_rects': self.game_state.pop('train_button_rects', {}),
                'pause_menu_button_rects': self.game_state.pop('pause_menu_button_rects', {})
            }

        try:
            data = {
                'grid': self.grid,
                'grid_width': self.num_tiles_x,
                'grid_height': self.num_tiles_y,
                'center_gold_flag': self.center_gold_flag,
                'players': self.players,
                'game_state': self.game_state
            }
            with open(full_path, 'wb') as f:
                pickle.dump(data, f)
            debug_print(f"Game map saved successfully to {full_path}.")
        finally:
            # Restore unpicklable objects
            if self.game_state:
                self.game_state.update(gui_state)

    def load_map(self, filename):
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
            
            # Store any existing GUI state before loading
            old_gui_state = None
            if self.game_state:
                old_gui_state = {
                    'screen': self.game_state.get('screen'),
                    'screen_width': self.game_state.get('screen_width'),
                    'screen_height': self.game_state.get('screen_height'),
                    'camera': self.game_state.get('camera'),
                    'minimap_panel_sprite': self.game_state.get('minimap_panel_sprite'),
                    'minimap_background': self.game_state.get('minimap_background'),
                    'minimap_entities_surface': self.game_state.get('minimap_entities_surface'),
                    'player_selection_surface': self.game_state.get('player_selection_surface')
                }

            # Load the data
            self.grid = data['grid']
            self.num_tiles_x = data['grid_width']
            self.num_tiles_y = data['grid_height']
            self.center_gold_flag = data['center_gold_flag']
            self.players = data['players']
            self.game_state = data.get('game_state', {})

            # Restore GUI state if it existed
            if old_gui_state:
                for key, value in old_gui_state.items():
                    if value is not None:
                        self.game_state[key] = value

            # Initialize old_resources if needed
            if self.game_state:
                self.game_state['old_resources'] = {
                    p.teamID: p.resources.copy() for p in self.players
                }

            # Reassign team IDs to match player positions
            for i, player in enumerate(self.players):
                player.teamID = i
                # Update team IDs for all entities belonging to this player
                for unit in player.units:
                    unit.team = i
                for building in player.buildings:
                    building.team = i

            # Update grid entities with new team IDs
            for entities in self.grid.values():
                for entity in entities:
                    if hasattr(entity, 'team') and entity.team is not None:
                        # Update entity's team ID to match its owner's new ID
                        for i, player in enumerate(self.players):
                            if entity in player.units or entity in player.buildings:
                                entity.team = i
                                break

            debug_print(f"Game map loaded successfully from {filename}.")
        except Exception as e:
            debug_print(f"Error loading game map: {e}")
            raise

    def move_to_inactive(self, entity):
        self.remove_entity(entity)
        pos = (round(entity.x), round(entity.y))
        if pos not in self.inactive_matrix:
            self.inactive_matrix[pos] = set()
        self.inactive_matrix[pos].add(entity)

    def remove_inactive(self, entity):
        pos = (round(entity.x), round(entity.y))
        self.inactive_matrix[pos].remove(entity)
        if not self.inactive_matrix[pos]:
            del self.inactive_matrix[pos]

    def add_projectile(self, projectile):
        self.projectiles[projectile.id] = projectile

    def remove_projectile(self, projectile):
        self.projectiles[projectile.id] = None
        del self.projectiles[projectile.id]

    def patch(self, dt):
        active_entities = set()
        for entities in self.grid.values():
            active_entities.update(entities)

        for entity in active_entities:
            entity.update(self, dt)
            if not entity.isAlive():
                self.move_to_inactive(entity)

        inactive_entities = set()
        for entities in self.inactive_matrix.values():
            inactive_entities.update(entities)

        for entity in inactive_entities:
            entity.update(self, dt)
            if not entity.state:
                self.remove_inactive(entity)
        projectiles = self.projectiles.copy()
        for projectile in projectiles.values():
            projectile.update(self, dt)
            if projectile.state == '':
                self.remove_projectile(projectile)

    def set_game_state(self, game_state):
        self.game_state = game_state