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

def random_map(width, height):
    grid = []  # Initialisation d'une nouvelle grille
    # Création d'une liste avec le bon nombre de chaque type de tuile
    tiles = (
        ['mountain'] * NUM_MOUNTAIN_TILES +
        ['gold'] * NUM_GOLD_TILES +
        ['wood'] * NUM_WOOD_TILES +
        ['food'] * NUM_FOOD_TILES
    )
    
    # Nombre total de tuiles
    total_tiles = (width // TILE_SIZE) * (height // TILE_SIZE)
    remaining_tiles = total_tiles - len(tiles)
    tiles += ['grass'] * remaining_tiles  # Ajoutez des tuiles de gazon pour combler les espaces

    # Mélanger la liste
    random.shuffle(tiles)

    # Remplir la grille comme une matrice 2D
    for y in range(height // TILE_SIZE):
        row = []
        for x in range(width // TILE_SIZE):
            terrain_type = tiles.pop()  # Récupérer une tuile de la liste mélangée
            row.append(Tile(terrain_type))
        grid.append(row)  # Ajouter la ligne complète à la grille

    return grid



class GameMap:
    def __init__(self, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height
        self.grid = random_map(width, height)  # Appelle random_map sans passer grid


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