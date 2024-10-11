# Models/Map.py

import random

# Constantes pour la carte
TILE_SIZE = 16  # Taille d'une tuile en pixels
MAP_WIDTH = 120 * TILE_SIZE  # 1920 pixels
MAP_HEIGHT = 120 * TILE_SIZE  # 1920 pixels

# Nombre de tuiles de chaque type
NUM_MOUNTAIN_TILES = 1000
NUM_GOLD_TILES = 1000
NUM_WOOD_TILES = 1000
NUM_FOOD_TILES = 1000

class Tile:
    def __init__(self, terrain_type, tile_size=TILE_SIZE):
        self.tile_size = tile_size
        self.terrain_type = terrain_type  # 'grass', 'mountain', 'gold', 'wood', 'food'
        self.building = None  # Pas de bâtiment
        self.unit = None      # Pas d'unité

    def is_walkable(self):
        return self.building is None

class GameMap:
    def __init__(self, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width  # en pixels
        self.height = height  # en pixels
        self.num_tiles_x = width // TILE_SIZE
        self.num_tiles_y = height // TILE_SIZE
        self.grid = self.random_map(self.num_tiles_x, self.num_tiles_y)

    def place_building(self, x, y, building):
        if self.grid[y][x].building is None:
            self.grid[y][x].building = building
            return True
        return False

    def place_unit(self, x, y, unit):
        if self.grid[y][x].unit is None and self.grid[y][x].is_walkable():
            self.grid[y][x].unit = unit
            return True
        return False

    def random_map(self, num_tiles_x, num_tiles_y):
        grid = []

        tiles = (
            ['mountain'] * NUM_MOUNTAIN_TILES +
            ['gold'] * NUM_GOLD_TILES +
            ['wood'] * NUM_WOOD_TILES +
            ['food'] * NUM_FOOD_TILES
        )

        # Nombre total de tuiles
        total_tiles = num_tiles_x * num_tiles_y
        remaining_tiles = total_tiles - len(tiles)
        tiles += ['grass'] * remaining_tiles  # Ajoute des tuiles d'herbe pour combler les espaces

        # Mélange la liste
        random.shuffle(tiles)

        for y in range(num_tiles_y):
            row = []
            for x in range(num_tiles_x):
                terrain_type = tiles.pop()  # Récupère une tuile de la liste mélangée
                row.append(Tile(terrain_type))
            grid.append(row)

        return grid

    def print_map(self):
        # Mapping des types de terrain aux acronymes
        terrain_acronyms = {
            'grass': '#',
            'mountain': 'M',
            'gold': 'G',
            'wood': 'W',
            'food': 'F'
        }

        for row in self.grid:
            row_display = []
            for tile in row:
                row_display.append(terrain_acronyms.get(tile.terrain_type, '?'))
            print(' '.join(row_display))
