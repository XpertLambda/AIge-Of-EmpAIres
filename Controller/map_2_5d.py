# Controller/map_2_5d.py
import pygame
from Models.Map import GameMap
from Settings.setup import TILE_SIZE

def to_isometric(x, y, tile_size):
    iso_x = (x - y) * (tile_size // 2)
    iso_y = (x + y) * (tile_size // 4)
    return iso_x, iso_y

def draw_map(screen, game_map, textures, camera):
    screen.fill((0, 0, 0))  # Effacer l'écran
    for y in range(game_map.height // TILE_SIZE):
        for x in range(game_map.width // TILE_SIZE):
            tile = game_map.grid[y][x]
            iso_x, iso_y = to_isometric(x, y, TILE_SIZE)
            color = (0, 0, 0)  # Couleur par défaut (noir)
            if tile.terrain_type == "grass":
                color = (34, 139, 34)  # Vert
            elif tile.terrain_type == "mountain":
                color = (139, 137, 137)  # Gris
            elif tile.terrain_type == "gold":
                color = (255, 215, 0)  # Or
            elif tile.terrain_type == "wood":
                color = (139, 69, 19)  # Marron
            elif tile.terrain_type == "food":
                color = (255, 0, 0)  # Rouge

            pygame.draw.polygon(screen, color, [
                (iso_x - camera.camera.x, iso_y - camera.camera.y),
                (iso_x + TILE_SIZE // 2 - camera.camera.x, iso_y + TILE_SIZE // 4 - camera.camera.y),
                (iso_x - camera.camera.x, iso_y + TILE_SIZE // 2 - camera.camera.y),
                (iso_x - TILE_SIZE // 2 - camera.camera.x, iso_y + TILE_SIZE // 4 - camera.camera.y)
            ])
    pygame.display.flip()  # Mets à jour l'affichage