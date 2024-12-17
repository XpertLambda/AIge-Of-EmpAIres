# Models/Map.py
# On modifie la logique de déploiement des joueurs pour qu'ils occupent
# chacun une zone carrée (ou rectangulaire) de la carte, en répartissant
# la carte en grille en fonction du nombre de joueurs.

import math
import random
import os
import pickle
import time
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
    def __init__(self, grid_size, gold_at_center, players, generate=True):
        self.grid_size = grid_size        # Store grid size
        self.gold_at_center = gold_at_center  # Store gold_at_center flag
        self.players = players            # Store players list
        self.num_tiles_x = grid_size
        self.num_tiles_y = grid_size
        self.num_tiles = self.num_tiles_x * self.num_tiles_y
        if generate:
            if gold_at_center:
                self.grid = self.random_map_gold(self.num_tiles_x, self.num_tiles_y, players)
            else:
                self.grid = self.random_map(self.num_tiles_x, self.num_tiles_y)
        else:
            self.grid = {}  # Initialize an empty grid

    def add_entity(self, grid, x, y, entity):
        if x < 0 or y < 0 or x + entity.size >= self.num_tiles_x or y + entity.size >= self.num_tiles_y:
            return False
        for i in range(entity.size):
            for j in range(entity.size):
                pos = (x + i, y + j)
                if pos in grid:
                    # Impossible de placer l'entité ici
                    return False
        # Placement effectif
        for i in range(entity.size):
            for j in range(entity.size):
                pos = (x + i, y + j)
                grid[pos] = set()
                grid[pos].add(entity)
        entity.x = x + (entity.size - 1)/2
        entity.y = y + (entity.size - 1)/2
        return True

    def remove_entity(self, grid, x, y, entity):
        if x < 0 or y < 0 or x + entity.size >= self.num_tiles_x or y + entity.size >= self.num_tiles_y:
            return False  # Position out of bounds
        for i in range(entity.size):
            for j in range(entity.size):
                pos = (x + i, y + j)
                if pos not in grid or entity not in grid[pos]:
                    return False  # Entity not present at the position
        # Remove entity from the grid
        for i in range(entity.size):
            for j in range(entity.size):
                pos = (x + i, y + j)
                grid[pos].remove(entity)
                if not grid[pos]:  # clean up the position if there is an empty set
                    del grid[pos]
        return True

    def generate_zones(self, num_players):
        # On veut répartir les joueurs dans une grille la plus carrée possible.
        # Nombre de colonnes = ceil(sqrt(num_players))
        # Nombre de lignes = ceil(num_players / cols)
        cols = int(math.ceil(math.sqrt(num_players)))
        rows = int(math.ceil(num_players / cols))

        zone_width = self.num_tiles_x // cols
        zone_height = self.num_tiles_y // rows

        zones = []
        # On crée une liste de zones (x_start, x_end, y_start, y_end) pour chaque joueur
        for i in range(num_players):
            row = i // cols
            col = i % cols
            x_start = col * zone_width
            y_start = row * zone_height
            x_end = x_start + zone_width
            y_end = y_start + zone_height
            # S'il reste de la place non utilisée (division non entière), c'est pas grave.
            # On se limite au sol de zone_width/zone_height.
            zones.append((x_start, x_end, y_start, y_end))
        return zones

    def generate_buildings(self, grid, players):
        num_players = len(players)
        zones = self.generate_zones(num_players)

        for index, player in enumerate(players):
            x_start, x_end, y_start, y_end = zones[index]

            for building in player.buildings:
                max_attempts = (x_end - x_start) * (y_end - y_start)
                attempts = 0
                placed = False
                while attempts < max_attempts:
                    x = random.randint(x_start, max(x_start, x_end - building.size))
                    y = random.randint(y_start, max(y_start, y_end - building.size))
                    placed = self.add_entity(grid, x, y, building)
                    if placed:
                        break
                    attempts += 1
                if not placed:
                    # Si impossible de placer le bâtiment dans cette zone
                    # On essaie juste sur la carte complète en dernier recours
                    for ty in range(self.num_tiles_y - building.size):
                        for tx in range(self.num_tiles_x - building.size):
                            placed = self.add_entity(grid, tx, ty, building)
                            if placed:
                                break
                        if placed:
                            break
                    if not placed:
                        raise ValueError("Unable to deploy building for a player; map too crowded?")

    def generate_units(self, grid, players):
        num_players = len(players)
        zones = self.generate_zones(num_players)

        for index, player in enumerate(players):
            x_start, x_end, y_start, y_end = zones[index]

            for unit in player.units:
                placed = False
                attempts = 0
                # On essaie de placer l'unité dans la zone du joueur
                while not placed and attempts < 1000:
                    x_unit = random.randint(x_start, x_end - 1)
                    y_unit = random.randint(y_start, y_end - 1)
                    placed = self.add_entity(grid, x_unit, y_unit, unit)
                    attempts += 1
                if not placed:
                    # Si non placé dans la zone, on tente globalement
                    attempts = 0
                    while not placed and attempts < 1000:
                        x_unit = random.randint(0, self.num_tiles_x - 1)
                        y_unit = random.randint(0, self.num_tiles_y - 1)
                        placed = self.add_entity(grid, x_unit, y_unit, unit)
                        attempts += 1
                    if not placed:
                        print(f"Warning: Failed to deploy unit for player {player.teamID} after multiple attempts.")

    def random_map(self, num_tiles_x, num_tiles_y):
        grid = {}
        self.generate_buildings(grid, self.players)  # Use self.players
        self.generate_units(grid, self.players)

        resource_classes = {
            'gold': Gold,
            'wood': Wood,
            'food': Food,
        }

        resources = (
            ['gold'] * NUM_GOLD_TILES +
            ['wood'] * NUM_WOOD_TILES +
            ['food'] * NUM_FOOD_TILES
        )
        random.shuffle(resources)

        for resource_type in resources:
            placed = False
            attempts = 0
            while not placed and attempts < 1000:
                x = random.randint(0, num_tiles_x - 1)
                y = random.randint(0, num_tiles_y - 1)
                resource_class = resource_classes[resource_type]
                resource = resource_class(x, y)
                placed = self.add_entity(grid, x, y, resource)
                attempts += 1
            if not placed:
                print(f"Warning: Failed to deploy {resource_type} after 1000 attempts.")
        return grid

    def random_map_gold(self, num_tiles_x, num_tiles_y, players):
        # On ne modifie pas la logique du spawn gold centré, uniquement l'assignation d'entités joueurs reste inchangée
        grid = {}

        resource_classes = {
            'gold': Gold,
            'wood': Wood,
            'food': Food,
        }

        # Placer l'or au centre
        resources = (
            ['gold'] * NUM_GOLD_TILES +
            ['wood'] * NUM_WOOD_TILES +
            ['food'] * NUM_FOOD_TILES
        )

        center_x = num_tiles_x // 2
        center_y = num_tiles_y // 2
        gold_count = 0
        layer = 0
        while gold_count < NUM_GOLD_TILES:
            for dx in range(-layer, layer + 1):
                for dy in range(-layer, layer + 1):
                    x = center_x + dx
                    y = center_y + dy
                    if 0 <= x < num_tiles_x and 0 <= y < num_tiles_y:
                        if (x, y) not in grid:
                            grid[(x, y)] = set()
                            if gold_count < NUM_GOLD_TILES:
                                resource = resource_classes['gold'](x, y)
                                grid[(x, y)].add(resource)
                                gold_count += 1
                                if gold_count >= NUM_GOLD_TILES:
                                    break
                if gold_count >= NUM_GOLD_TILES:
                    break
            layer += 1

        # Place other resources randomly
        for resource_type in resources:
            if resource_type == 'gold':
                continue
            placed = False
            attempts = 0
            while not placed and attempts < 1000:
                x = random.randint(0, num_tiles_x - 1)
                y = random.randint(0, num_tiles_y - 1)
                if (x, y) not in grid:
                    grid[(x, y)] = set()
                    resource_class = resource_classes[resource_type]
                    resource = resource_class(x, y)
                    grid[(x, y)].add(resource)
                    placed = True
                attempts += 1
            if not placed:
                print(f"Warning: Failed to place {resource_type} after 1000 attempts.")

        # Déploiement des entités joueurs
        self.generate_buildings(grid, players)
        self.generate_units(grid, players)

        return grid

    def print_map(self):
        for y in range(self.num_tiles_y):
            row_display = []
            for x in range(self.num_tiles_x):
                pos = (x, y)
                if pos in self.grid:
                    entities = self.grid[pos]
                    # On affiche juste le premier acronyme
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
            'gold_at_center': self.gold_at_center,
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
            self.gold_at_center = data['gold_at_center']
            self.players = data['players']
            self.num_tiles_x = self.num_tiles_y = self.grid_size
            print(f"Game map loaded successfully from {filename}.")
        except Exception as e:
            print(f"Error loading game map: {e}")

    def display_map_in_terminal(self):
        """
        Affiche une représentation textuelle de la carte dans le terminal.
        """
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
