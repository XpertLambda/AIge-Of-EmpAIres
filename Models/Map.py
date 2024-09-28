import random
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
    def __init__(self, numberOfPlayers=2, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height
        self.numberOfPlayers = numberOfPlayers
        self.grid = self.random_map(width, height)  


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
    
    def random_map(self, width, height):
        grid = [] 

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

        # Mélange la liste
        random.shuffle(tiles)

        for y in range(height // TILE_SIZE):
            row = []
            for x in range(width // TILE_SIZE):
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
                row_display.append(terrain_acronyms.get(tile.terrain_type, '??'))
            print(''.join(row_display))