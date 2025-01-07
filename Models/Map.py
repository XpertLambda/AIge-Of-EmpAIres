import math
import random
import os
import pickle
import time
from collections import defaultdict
from datetime import datetime
from Entity.Building import *
from Entity.Unit import *
from Entity.Resource.Resource import *
from Entity.Resource.Gold import Gold
from Entity.Resource.Tree import Tree
from Settings.setup import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, NUM_GOLD_TILES, NUM_WOOD_TILES, NUM_FOOD_TILES, GOLD_SPAWN_MIDDLE, SAVE_DIRECTORY

class GameMap:
    def __init__(self, grid_size, center_gold_flag, players, generate=True):
        self.grid_size = grid_size
        self.center_gold_flag = center_gold_flag
        self.players = players
        self.num_tiles_x = grid_size
        self.num_tiles_y = grid_size
        self.num_tiles = self.num_tiles_x * self.num_tiles_y
        self.grid = {}
        if generate:
            self.generate_map()

    def add_entity(self, entity, x, y):
        if x < 0 or y < 0 or x + entity.size >= self.num_tiles_x or y + entity.size >= self.num_tiles_y:
            return False
        rounded_x, rounded_y = round(x), round(y)
        for i in range(entity.size):
            for j in range(entity.size):
                pos = (rounded_x + i, rounded_y + j)
                if pos in self.grid:
                    return False

        for i in range(entity.size):
            for j in range(entity.size):
                pos = (rounded_x + i, rounded_y + j)
                self.grid[pos] = set()
                self.grid[pos].add(entity)
        entity.x = x + (entity.size - 1)/2
        entity.y = y + (entity.size - 1)/2
        return True

    def remove_entity(self, entity, x, y):
        if x < 0 or y < 0 or x + entity.size >= self.num_tiles_x or y + entity.size >= self.num_tiles_y:
            return False
        rounded_x, rounded_y = round(x), round(y)
        for i in range(entity.size):
            for j in range(entity.size):
                pos = (rounded_x + i, rounded_y + j)
                if pos not in self.grid or entity not in self.grid[pos]:
                    return False  # Entity not present at the position

        for i in range(entity.size):
            for j in range(entity.size):
                pos = (rounded_x + i, rounded_y + j)
                self.grid[pos].remove(entity)
                if not self.grid[pos]:  
                    del self.grid[pos]
        return True

    def generate_zones(self, num_players):
        cols = int(math.ceil(math.sqrt(num_players)))
        rows = int(math.ceil(num_players / cols))
        zone_width = self.num_tiles_x // cols
        zone_height = self.num_tiles_y // rows
        zones = []

        for i in range(num_players):
            row = i // cols
            col = i % cols
            x_start = col * zone_width
            y_start = row * zone_height
            x_end = x_start + zone_width
            y_end = y_start + zone_height

            zones.append((x_start, x_end, y_start, y_end))
        return zones

    def generate_buildings(self, players):
        num_players = len(players)
        global zones
        zones = self.generate_zones(num_players)

        for index, player in enumerate(players):
            x_start, x_end, y_start, y_end = zones[player.teamID]
            for building in player.buildings:
                max_attempts = (x_end - x_start) * (y_end - y_start)
                attempts = 0
                placed = False
                while attempts < max_attempts:
                    x = random.randint(x_start, max(x_start, x_end - building.size))
                    y = random.randint(y_start, max(y_start, y_end - building.size))
                    placed = self.add_entity(building, x, y)
                    if placed:
                        if (isinstance(building, TownCentre) or isinstance(building, House)):
                            player.maximum_population += building.population
                        break
                    attempts += 1
              
                if not placed:
                    for tile_y in range(self.num_tiles_y - building.size):
                        for tile_x in range(self.num_tiles_x - building.size):
                            placed = self.add_entity(building, tile_x, tile_y, building)
                            if placed:
                                break
                        if placed:
                            break
                    if not placed:
                        raise ValueError("Unable to deploy building for a player; map too crowded?")

    def generate_units(self, players):
        num_players = len(players)
        zones = self.generate_zones(num_players)

        for index, player in enumerate(players):
            x_start, x_end, y_start, y_end = zones[index]

            for unit in player.units:
                placed = False
                attempts = 0
                while not placed and attempts < 1000:
                    x_unit = random.randint(x_start, x_end - 1)
                    y_unit = random.randint(y_start, y_end - 1)
                    placed = self.add_entity(unit, x_unit, y_unit)
                    attempts += 1
                if not placed:
                    attempts = 0
                    while not placed and attempts < 1000:
                        x_unit = random.randint(0, self.num_tiles_x - 1)
                        y_unit = random.randint(0, self.num_tiles_y - 1)
                        placed = self.add_entity(unit, x_unit, y_unit)
                        attempts += 1
                    if not placed:
                        print(f"Warning: Failed to deploy unit for player {player.teamID} after multiple attempts.")

    def generate_map(self):
        #self.generate_resources(grid)
        self.generate_buildings(self.players)
        self.generate_units(self.players)

    def generate_resources(self):
        resource_classes = {
            'gold': Gold,
            'wood': Tree
        }
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
            # Place gold randomly
            for _ in range(NUM_GOLD_TILES):
                placed = False
                attempts = 0
                while not placed and attempts < 1000:
                    x = random.randint(0, self.num_tiles_x - 1)
                    y = random.randint(0, self.num_tiles_y - 1)
                    resource = resource_classes['gold'](x, y)
                    placed = self.add_entity(resource, x, y)
                    attempts += 1

        # Generate trees as groups instead of one by one
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


    def print_map(self):
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
            print(''.join(row_display))
    
    def save_map(self, filename=None):
        if filename is None:
            # Automatic filename generation with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"save_{timestamp}.pkl"
        else:
            # Ensure the filename ends with .pkl
            if not filename.endswith('.pkl'):
                filename += '.pkl'
        full_path = os.path.join(SAVE_DIRECTORY, filename)

        data = {
            'grid': self.grid,
            'grid_size': self.grid_size,
            'center_gold_flag': self.center_gold_flag,
            'players': self.players
        }
        with open(full_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Game map saved successfully to {full_path}.")

    def load_map(self, filename):
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
            self.grid = data['grid']
            self.grid_size = data['grid_size']
            self.center_gold_flag = data['center_gold_flag']
            self.players = data['players']
            self.num_tiles_x = self.num_tiles_y = self.grid_size
            print(f"Game map loaded successfully from {filename}.")
        except Exception as e:
            print(f"Error loading game map: {e}")

    def update_terminal(self):
        """
        Affiche une représentation textuelle de la carte dans le terminal.
        """
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the terminal
        for y in range(self.num_tiles_y):
            row = ''
            for x in range(self.num_tiles_x):
                entities = self.grid.get((x, y), None)
                if entities:
                    # Use the acronym of the first entity on the tile
                    entity = next(iter(entities))
                    row += entity.acronym
                else:
                    row += ' '
            print(row)

   #ne marche pas
    def place_building(self,building,team):
        #placer un building au hasard
        x_start, x_end, y_start, y_end = zones[team.teamID]
        max_attempts = (x_end - x_start) * (y_end - y_start)
        attempts = 0
        placed = False
        while attempts < max_attempts:
            x = random.randint(x_start, max(x_start, x_end - building.size))
            y = random.randint(y_start, max(y_start, y_end - building.size))
            placed = self.add_entity( building, x, y)
            if placed:
                return True
            attempts += 1
        if not placed:
            # Si impossible de placer le bâtiment dans cette zone
            # On essaie juste sur la carte complète en dernier recours
            for ty in range(self.num_tiles_y - building.size):
                for tx in range(self.num_tiles_x - building.size):
                    placed = self.add_entity(building, tx, ty)
                    if placed:
                        break
            if placed:
                return True
            if not placed:
                return False
