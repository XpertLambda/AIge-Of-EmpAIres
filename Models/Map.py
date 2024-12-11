# Models/Map.py
import random
import os
import pickle
from collections import defaultdict
from datetime import datetime
from Entity.Building import Building
from Entity.Unit import *
from Entity.Resource.Resource import *
from Entity.Resource.Gold import Gold
from Entity.Resource.Wood import Wood
from Entity.Resource.Food import Food
from Settings.setup import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, NUM_GOLD_TILES, NUM_WOOD_TILES, NUM_FOOD_TILES, GOLD_SPAWN_MIDDLE

class GameMap:
    def __init__(self, players, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height
        self.num_tiles_x = width // TILE_SIZE
        self.num_tiles_y = height // TILE_SIZE
        self.players = players
        if GOLD_SPAWN_MIDDLE:
            self.grid = self.random_map_gold(self.num_tiles_x, self.num_tiles_y, players)
        else:
            self.grid = self.random_map(self.num_tiles_x, self.num_tiles_y, players)

    def add_entity(self, grid, x,  y,  entity):
        if x < 0 or y < 0 or x + entity.size >= self.num_tiles_x or y + entity.size >= self.num_tiles_y:
            return False
        for i in range(entity.size):
            for j in range(entity.size):
                pos = (x + i, y + j)
                grid_entities = grid.get(pos, None)
                if grid_entities:
                    return False

        for i in range(entity.size):
            for j in range(entity.size):
                pos = (x + i, y + j)
                grid[pos] = set()
                grid[pos].add(entity)
        entity.x = x + (entity.size - 1)/2
        entity.y = y + (entity.size - 1)/2
        return True

    def generate_buildings(self, grid, players):
        num_players = len(players)
        zone_width = self.num_tiles_x // (num_players if num_players % 2 == 0 else 1)
        zone_height = self.num_tiles_y // (num_players if num_players % 2 == 0 else 1)

        for index, player in enumerate(players):
            x_start = (index % (num_players // 2)) * zone_width if num_players > 1 else 0
            y_start = (index // (num_players // 2)) * zone_height if num_players > 1 else 0
            x_end = x_start + zone_width if num_players > 1 else self.num_tiles_x
            y_end = y_start + zone_height if num_players > 1 else self.num_tiles_y

            for building in player.buildings:
                max_attempts = zone_width * zone_height if num_players > 1 else (self.num_tiles_x * self.num_tiles_y)
                attempts = 0
                placed = False

                while attempts < max_attempts:
                    x = random.randint(x_start, x_end - building.size)
                    y = random.randint(y_start, y_end - building.size)
                    placed = self.add_entity(grid, x, y, building)
                    if placed:
                        break
                    attempts += 1

                if not placed:
                    for y_pos in range(y_start, y_end - building.size + 1):
                        for x_pos in range(x_start, x_end - building.size + 1):
                            placed = self.self.add_entity(grid, x_pos, y_pos, building)
                            if placed:
                                break
                if not placed:
                    raise ValueError("Unable to deploy building in player zone; zone might be fully occupied.")
    
    def generate_units(self, grid, players):
        num_players = len(players)
        zone_width = self.num_tiles_x // (num_players if num_players % 2 == 0 else 1)
        zone_height = self.num_tiles_y // (num_players if num_players % 2 == 0 else 1)
        
        for index, player in enumerate(players):
            x_start = (index % (num_players // 2)) * zone_width if num_players > 1 else 0
            y_start = (index // (num_players // 2)) * zone_height if num_players > 1 else 0
            x_end = x_start + zone_width if num_players > 1 else self.num_tiles_x
            y_end = y_start + zone_height if num_players > 1 else self.num_tiles_y
            
            for unit in player.units:
                placed = False
                attempts = 0
                while not placed and attempts < 1000:
                    x_unit = random.randint(x_start, x_end - 1)
                    y_unit = random.randint(y_start, y_end - 1)
                    placed = self.add_entity(grid, x_unit, y_unit, unit)
                    if placed:
                        break
                    attempts += 1

                if not placed:
                    print(f"Warning: Failed to deploy villager for player {player.teamID} after 1000 attempts.")

    def random_map(self, num_tiles_x, num_tiles_y, players):
        grid = {}

        # Generate buildings for all players
        self.generate_buildings(grid, players)
        self.generate_units(grid, players)

        # Map resource types to their respective classes
        resource_classes = {
            'gold': Gold,
            'wood': Wood,
            'food': Food,
        }

        # Create a list of resources to place
        resources = (
            ['gold'] * NUM_GOLD_TILES +
            ['wood'] * NUM_WOOD_TILES +
            ['food'] * NUM_FOOD_TILES
        )
        random.shuffle(resources)

        # Place resources on the grid
        for resource_type in resources:
            placed = False
            attempts = 0

            while not placed and attempts < 1000:
                # Random position within the map bounds
                x = random.randint(0, num_tiles_x - 1)
                y = random.randint(0, num_tiles_y - 1)
                pos = (x, y)
                resource_class = resource_classes[resource_type]
                resource = resource_class(x, y)
                placed = self.add_entity(grid, x, y, resource)
                if placed:
                    break
                attempts += 1

            if not placed:
                print(f"Warning: Failed to deploy {resource_type} after 1000 attempts.")
        return grid

    def print_map(self):
        # Iterate over the grid by rows and columns
        for y in range(self.num_tiles_y):
            row_display = []
            for x in range(self.num_tiles_x):
                pos = (x, y)

                # Check if the position exists in the grid
                if pos in self.grid:
                    # Retrieve the entities at this position
                    entities = self.grid[pos]

                    for entity in entities :
                        row_display.append(entity.acronym)
                else:
                    # Default for uninitialized tiles
                    row_display.append(' ')

            # Print the row as a string
            print(''.join(row_display))
    
    def random_map_gold(self, num_tiles_x, num_tiles_y, players):
        grid = {}

        # Map resource types to their respective classes
        resource_classes = {
            'gold': Gold,
            'wood': Wood,
            'food': Food,
        }

        # Create a list of resources to place
        resources = (
            ['gold'] * NUM_GOLD_TILES +
            ['wood'] * NUM_WOOD_TILES +
            ['food'] * NUM_FOOD_TILES
        )

        # Place gold resources in a central square
        center_x = num_tiles_x // 2
        center_y = num_tiles_y // 2
        gold_count = 0
        layer = 0

        while gold_count < NUM_GOLD_TILES:
            # Iterate over the current square layer
            for dx in range(-layer, layer + 1):
                for dy in range(-layer, layer + 1):
                    x = center_x + dx
                    y = center_y + dy
                    pos = (x, y)

                    # Ensure we don't exceed the map boundaries
                    if 0 <= x < num_tiles_x and 0 <= y < num_tiles_y:
                        # Check if the position is valid for placement
                        if pos not in grid:
                            grid[pos] = set()
                            
                            # Place gold if the maximum count is not reached
                            if gold_count < NUM_GOLD_TILES:
                                resource = resource_classes['gold'](x, y)
                                grid[pos].add(resource)
                                gold_count += 1
                                if gold_count >= NUM_GOLD_TILES:
                                    break
                if gold_count >= NUM_GOLD_TILES:
                    break
            layer += 1

        # Place other resources randomly
        for resource_type in resources:
            if resource_type == 'gold':
                continue  # Skip gold as it is already placed deterministically

            placed = False
            attempts = 0

            while not placed and attempts < 1000:
                # Random position within the map bounds
                x = random.randint(0, num_tiles_x - 1)
                y = random.randint(0, num_tiles_y - 1)
                pos = (x, y)

                # Check if the position is valid
                if pos not in grid:
                    grid[pos] = set()
                    # Create a new resource and place it
                    resource_class = resource_classes[resource_type]
                    resource = resource_class(x, y)
                    grid[pos].add(resource)
                    placed = True

                attempts += 1

            if not placed:
                print(f"Warning: Failed to place {resource_type} after 1000 attempts.")

        # Generate buildings for all players
        self.building_generation(grid, players)

        return grid

    def save_map(self, directory='saves'):
        if not os.path.exists(directory):
            os.makedirs(directory)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(directory, f'save_{timestamp}.pkl')
        game_state = {
            'players': self.players,
            'tiles': self.grid
        }
        try:
            with open(filename, 'wb') as file:
                pickle.dump(game_state, file)
            print(f"Game map saved successfully to {filename}.")
        except Exception as e:
            print(f"Error saving game map: {e}")

    def load_map(self, filename):
        try:
            with open(filename, 'rb') as file:
                game_state = pickle.load(file)
            self.players = game_state['players']
            self.grid = game_state['tiles']
            for tile in self.grid.values():
                tile.mark_dirty()
            print(f"Game map loaded successfully from {filename}.")
        except Exception as e:
            print(f"Error loading game map: {e}")