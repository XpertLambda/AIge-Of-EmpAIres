# Models/Map.py
import random
import os
import pickle
from collections import defaultdict
from datetime import datetime
from Entity.Building import Building
from Entity.Unit import Unit
from Entity.Resource.Resource import *
from Entity.Resource.Gold import Gold
from Entity.Resource.Wood import Wood
from Entity.Resource.Food import Food
from Settings.setup import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, NUM_GOLD_TILES, NUM_WOOD_TILES, NUM_FOOD_TILES

class GameMap:
    def __init__(self, players, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height
        self.num_tiles_x = width // TILE_SIZE
        self.num_tiles_y = height // TILE_SIZE
        self.players = players
        self.grid = self.random_map(self.num_tiles_x, self.num_tiles_y, players)

    def place_building(self, x, y, building):
        pass

    def place_unit(self, x, y, unit):
        pass

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
            print(f"Game map loaded successfully from {filename}.")
        except Exception as e:
            print(f"Error loading game map: {e}")

    def building_generation(self, grid, players):
        num_players = len(players)
        zone_width = self.num_tiles_x // (num_players if num_players % 2 == 0 else 1)
        zone_height = self.num_tiles_y // (num_players if num_players % 2 == 0 else 1)

        for index, player in enumerate(players):
            x_start = (index % (num_players // 2)) * zone_width
            y_start = (index // (num_players // 2)) * zone_height
            x_end = x_start + zone_width
            y_end = y_start + zone_height

            for building in player.buildings:
                max_attempts = zone_width * zone_height
                attempts = 0
                placed = False

                while attempts < max_attempts:
                    x = random.randint(x_start, x_end - building.size)
                    y = random.randint(y_start, y_end - building.size)
                    if self.can_place_building(grid, x, y, building):
                        placed = True
                        break
                    attempts += 1

                if not placed:
                    for y_pos in range(y_start, y_end - building.size + 1):
                        for x_pos in range(x_start, x_end - building.size + 1):
                            if self.can_place_building(grid, x_pos, y_pos, building):
                                x, y = x_pos, y_pos
                                placed = True
                                break
                        if placed:
                            break

                if not placed:
                    raise ValueError("Unable to place building in player zone; zone might be fully occupied.")

                for i in range(building.size):
                    for j in range(building.size):
                        pos = (x + i, y + j)
                        if pos not in grid:
                            grid[pos] = set()
                        grid[pos].add(building)
                building.x = x
                building.y = y

    def can_place_building(self, grid, x, y, building):
        if x + building.size > self.num_tiles_x or y + building.size > self.num_tiles_y:
            return False

        for dx in range(building.size):
            for dy in range(building.size):
                position = (x + dx, y + dy)
                if position in grid:
                    for entity in grid[position]:
                        # Conflict if the cell contains a non-walkable entity
                        if isinstance(entity, (Unit, Resource, Building)):
                            if not building.is_walkable or isinstance(entity, Building):
                                return False
        return True

    def random_map(self, num_tiles_x, num_tiles_y, players):
        grid = {}

        # Generate buildings for all players
        self.building_generation(grid, players)

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

                # Check if the position is valid
                if pos not in grid:
                    grid[pos] = set()
                if all(not isinstance(entity, Building) for entity in grid[pos]):
                    # Create a new resource and place it
                    resource_class = resource_classes[resource_type]
                    resource = resource_class(x, y)
                    grid[pos].add(resource)
                    placed = True

                attempts += 1

            if not placed:
                print(f"Warning: Failed to place {resource_type} after 1000 attempts.")

        return grid

    def get_tile(self, x, y):
        pos = (x, y)
        tile = self.grid.get(pos)
        return tile

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

