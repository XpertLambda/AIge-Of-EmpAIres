# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/Projet_python\Models\Map.py
import random
import os
import pickle
from datetime import datetime
from Models.Building import Building
from Settings.setup import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, NUM_GOLD_TILES, NUM_WOOD_TILES, NUM_FOOD_TILES

class Tile:
    def __init__(self, terrain_type, tile_size=TILE_SIZE):
        self.tile_size = tile_size
        self.terrain_type = terrain_type
        self.building = None
        self.unit = None
        self.player = None
        self.dirty = True

    def is_walkable(self):
        return self.building is None

    def mark_dirty(self):
        self.dirty = True

# Tile global pour l'herbe, jamais dirty, utilisé par défaut
GLOBAL_GRASS_TILE = Tile('grass')
GLOBAL_GRASS_TILE.dirty = False

class GameMap:
    def __init__(self, players, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height
        self.num_tiles_x = width // TILE_SIZE
        self.num_tiles_y = height // TILE_SIZE
        self.players = players

        self.grid = {}

        self.random_map(width, height, players)

    def place_building(self, x, y, building):
        for i in range(building.size1):
            for j in range(building.size2):
                pos = (x + i, y + j)
                t = self.grid.get(pos)
                if t is None:
                    t = Tile('grass')
                t.building = building
                t.terrain_type = building.acronym
                t.player = getattr(building, 'player', None)
                t.mark_dirty()
                self.grid[pos] = t

    def place_unit(self, x, y, unit):
        pos = (x, y)
        t = self.grid.get(pos)
        if t is None:
            t = Tile('grass')
        t.unit = unit
        t.mark_dirty()
        self.grid[pos] = t

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

    def building_generation(self, grid, players):
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
                    x = random.randint(x_start, max(x_end - building.size1, x_start))
                    y = random.randint(y_start, max(y_end - building.size2, y_start))
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
                        t = grid.get(pos)
                        if t is None:
                            t = Tile('grass')
                        t.building = building
                        t.terrain_type = building.acronym
                        t.player = player
                        t.mark_dirty()
                        grid[pos] = t
                        building.x = x
                        building.y = y

    def can_place_building(self, grid, x, y, building):
        if x + building.size1 > self.num_tiles_x or y + building.size2 > self.num_tiles_y:
            return False
        for i in range(building.size1):
            for j in range(building.size2):
                pos = (x + i, y + j)
                tile = grid.get(pos)
                if tile and (tile.building is not None or tile.terrain_type in ['gold', 'wood', 'food']):
                    return False
        return True

    def random_map(self, width, height, players):
        self.building_generation(self.grid, players)

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
                tile = self.grid.get(pos)
                if tile is None:
                    tile = Tile(terrain_type)
                    tile.mark_dirty()
                    self.grid[pos] = tile
                    placed = True
                else:
                    if tile.terrain_type == 'grass' and tile.building is None:
                        tile.terrain_type = terrain_type
                        tile.mark_dirty()
                        placed = True

    def get_tile(self, x, y):
        pos = (x, y)
        # Retourne le tile global d'herbe si non trouvé
        return self.grid.get(pos, GLOBAL_GRASS_TILE)

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
