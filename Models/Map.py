import random
from Models.Building import Building
from Settings.setup import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, NUM_MOUNTAIN_TILES, NUM_GOLD_TILES, NUM_WOOD_TILES, NUM_FOOD_TILES

class Tile:
    def __init__(self, terrain_type, tile_size=TILE_SIZE):
        self.tile_size = tile_size
        self.terrain_type = terrain_type  # Grass, Mountain, Gold, Wood, Food
        self.building = None    # Tuile sans bâtiment
        self.unit = None        # Tuile sans unité

    def is_walkable(self):
        return self.building is None




class GameMap:
    def __init__(self, players, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height
        self.players = players
        self.grid = self.random_map(width, height, players)  

    def place_building(self, x, y, building):
        pass

    def place_unit(self, x, y, unit):
        pass

    def building_generation(self, grid, players):
        for player in players:
            for building in player.buildings:
                attempts = 0
                max_attempts = 1000  # Nombre maximum de tentatives pour placer un bâtiment
                x, y = 0, 0  # initialisation
                while grid[y][x].building is not None and attempts < max_attempts:
                    x = random.randint(0, self.width // TILE_SIZE - 1)
                    y = random.randint(0, self.height // TILE_SIZE - 1)
                    attempts += 1
                if attempts == max_attempts:
                    raise ValueError("Unable to place building, grid might be fully occupied.")
                print(x, y)
                grid[y][x].building = building
                grid[y][x].terrain_type = building.acronym

    def random_map(self, width, height, players):
        # Créer une grille vide initiale
        grid = [[Tile('empty') for _ in range(width // TILE_SIZE)] for _ in range(height // TILE_SIZE)]

        # Générer les bâtiments sur cette grille vide
        self.building_generation(grid, players)

        # Liste des types de terrain à placer
        tiles = (
            ['mountain'] * NUM_MOUNTAIN_TILES +
            ['gold'] * NUM_GOLD_TILES +
            ['wood'] * NUM_WOOD_TILES +
            ['food'] * NUM_FOOD_TILES
        )

        # Nombre total de tuiles
        total_tiles = (width // TILE_SIZE) * (height // TILE_SIZE)
        remaining_tiles = total_tiles - len(tiles)
        tiles += ['grass'] * remaining_tiles  # Ajoute des tuiles d'herbe pour combler les espaces

        # Mélanger les tuiles
        random.shuffle(tiles)

        # Remplir la grille avec les types de terrain
        for y in range(height // TILE_SIZE):
            for x in range(width // TILE_SIZE):
                terrain_type = tiles.pop()  # Prendre une tuile de la liste mélangée
                grid[y][x].terrain_type = terrain_type

        return grid

    def print_map(self):
        # Mapping des types de terrain aux acronymes
        terrain_acronyms = {
            'grass': ' ',
            'mountain': 'M',
            'gold': 'G',
            'wood': 'W',
            'food': 'F', 
            'town_centre': 'T',
        }

        for row in self.grid:
            row_display = []
            for tile in row:
                row_display.append(terrain_acronyms.get(tile.terrain_type, '??'))
            print(''.join(row_display))
           
    