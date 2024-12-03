# Models/Map.py

import random
import os
import pickle
from datetime import datetime
from Models.Building import Building
from Settings.setup import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, NUM_GOLD_TILES, NUM_WOOD_TILES, NUM_FOOD_TILES

class Tile:
    def __init__(self, terrain_type, tile_size=TILE_SIZE):
        self.tile_size = tile_size
        self.terrain_type = terrain_type  # 'grass', 'gold', 'wood', 'food'
        self.building = None  # Pas de bâtiment
        self.unit = None      # Pas d'unité
        self.player = None    # Propriétaire du terrain

    def is_walkable(self):
        return self.building is None

class GameMap:
    def __init__(self, players, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height
        self.num_tiles_x = width // TILE_SIZE
        self.num_tiles_y = height // TILE_SIZE
        self.players = players
        self.grid = self.random_map(width, height, players)

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
                    x = random.randint(x_start, x_end - building.size1)
                    y = random.randint(y_start, y_end - building.size2)
                    if self.can_place_building(grid, x, y, building):
                        placed = True
                        break
                    attempts += 1

                if not placed:
                    for y_pos in range(y_start, y_end - building.size2 + 1):
                        for x_pos in range(x_start, x_end - building.size1 + 1):
                            if self.can_place_building(grid, x_pos, y_pos, building):
                                x, y = x_pos, y_pos
                                placed = True
                                break
                        if placed:
                            break

                if not placed:
                    raise ValueError("Unable to place building in player zone; zone might be fully occupied.")

                for i in range(building.size1):
                    for j in range(building.size2):
                        pos = (x + i, y + j)
                        if pos not in grid:
                            grid[pos] = Tile('grass')
                        grid[pos].building = building
                        grid[pos].terrain_type = building.acronym
                        grid[pos].player = player
                        building.x = x
                        building.y = y

    def can_place_building(self, grid, x, y, building):
        if x + building.size1 > self.num_tiles_x or y + building.size2 > self.num_tiles_y:
            return False
        for i in range(building.size1):
            for j in range(building.size2):
                pos = (x + i, y + j)
                tile = grid.get(pos)
                if tile is not None and (tile.building is not None or tile.terrain_type in ['gold', 'wood', 'food']):
                    return False
        return True

    def random_map(self, width, height, players):
        grid = {}
        self.building_generation(grid, players)

        tiles = (
            ['gold'] * NUM_GOLD_TILES +
            ['wood'] * NUM_WOOD_TILES +
            ['food'] * NUM_FOOD_TILES
        )

        random.shuffle(tiles)

        for terrain_type in tiles:
            placed = False
            while not placed:
                x = random.randint(0, self.num_tiles_x - 1)
                y = random.randint(0, self.num_tiles_y - 1)
                pos = (x, y)
                tile = grid.get(pos)
                if tile is None:
                    grid[pos] = Tile(terrain_type)
                    placed = True
                elif tile.terrain_type == 'grass' and tile.building is None:
                    tile.terrain_type = terrain_type
                    placed = True

        return grid

    def get_tile(self, x, y):
        pos = (x, y)
        tile = self.grid.get(pos)
        if tile is None:
            tile = Tile('grass')
        return tile

    def print_map(self):
        terrain_acronyms = {
            'grass': ' ',
            'gold': 'G',
            'wood': 'W',
            'food': 'F',
        }

        for y in range(self.num_tiles_y):
            row_display = []
            for x in range(self.num_tiles_x):
                tile = self.grid.get((x, y))
                if tile is not None:
                    if tile.building is not None:
                        row_display.append(tile.building.acronym)
                    else:
                        row_display.append(terrain_acronyms.get(tile.terrain_type, '??'))
                else:
                    row_display.append(' ')
            print(''.join(row_display))
