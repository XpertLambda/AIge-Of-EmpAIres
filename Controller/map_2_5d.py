import pygame
from Settings.setup import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT

def to_isometric(x, y, tile_size):
    iso_x = (x - y) * (tile_size // 2)
    iso_y = (x + y) * (tile_size // 4)
    return iso_x, iso_y

def draw_map(screen, game_map, textures, camera):
    screen.fill((0, 0, 0))  # Effacer l'écran
    num_tiles_x = game_map.width // TILE_SIZE
    num_tiles_y = game_map.height // TILE_SIZE

    for y in range(num_tiles_y):
        for x in range(num_tiles_x):
            tile = game_map.grid[y][x]
            iso_x, iso_y = to_isometric(x, y, TILE_SIZE)
            iso_x, iso_y = camera.apply_zoom((iso_x, iso_y))
            screen_x = iso_x - camera.camera.x
            screen_y = iso_y - camera.camera.y

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

            # Dessiner le losange isométrique
            pygame.draw.polygon(screen, color, [
                (screen_x, screen_y),
                (screen_x + (TILE_SIZE // 2) * camera.zoom, screen_y + (TILE_SIZE // 4) * camera.zoom),
                (screen_x, screen_y + (TILE_SIZE // 2) * camera.zoom),
                (screen_x - (TILE_SIZE // 2) * camera.zoom, screen_y + (TILE_SIZE // 4) * camera.zoom)
            ])
    pygame.display.flip()
