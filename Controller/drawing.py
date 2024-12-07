# Controller/drawing.py

import pygame
import math
from Settings.setup import (
    HALF_TILE_SIZE,
    MINIMAP_MARGIN,
    MINIMAP_WIDTH,
    MINIMAP_HEIGHT,
    MAP_PADDING,
)
from Entity.Unit import Unit
from Entity.Building import Building
from Controller.isometric_utils import (
    to_isometric,
    get_color_for_terrain,
    screen_to_tile,
    tile_to_screen,
)
from Controller.init_sprites import *

def draw_map(screen, screen_width, screen_height, game_map, camera, players):
    """
    Dessine uniquement les sprites sur la carte isométrique visible à l'écran.
    """
    corners_screen = [
        (0, 0),  # Haut-gauche
        (screen_width, 0),  # Haut-droit
        (0, screen_height),  # Bas-gauche
        (screen_width, screen_height)  # Bas-droit
    ]

    tile_indices = [
        screen_to_tile(sx, sy, screen_width, screen_height, camera, HALF_TILE_SIZE / 2, HALF_TILE_SIZE / 4)
        for sx, sy in corners_screen
    ]

    x_indices = [tile_x for tile_x, _ in tile_indices]
    y_indices = [tile_y for _, tile_y in tile_indices]

    margin = 5  # Ajuster si nécessaire

    min_tile_x = max(0, min(x_indices) - margin)
    max_tile_x = min(game_map.num_tiles_x - 1, max(x_indices) + margin)
    min_tile_y = max(0, min(y_indices) - margin)
    max_tile_y = min(game_map.num_tiles_y - 1, max(y_indices) + margin)
    visible_entites = set()

    for y in range(min_tile_y, max_tile_y):
        for x in range(min_tile_x, max_tile_x):
            if x % 10 == 0 and y %10 == 0:   
                screen_x, screen_y = tile_to_screen(x+4.5, y+4.5, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
                fill_grass(screen, screen_x, screen_y, camera)
                #pygame.draw.circle(screen, (255,0,255), (screen_x, screen_y), 20*camera.zoom, 0)

            entities = game_map.grid.get((x, y), None)
            if entities:
                for entity in entities:
                    visible_entites.add(entity)
   
    for entity in sorted(visible_entites, key=lambda entity: (entity.x + entity.y)):
        entity.display(screen, screen_width, screen_height, camera)

def compute_map_bounds(game_map):
    """
    Calcule les limites de la carte en coordonnées isométriques.
    """
    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2

    num_tiles_x = game_map.num_tiles_x
    num_tiles_y = game_map.num_tiles_y

    corners = [
        (0, 0),
        (0, num_tiles_y - 1),
        (num_tiles_x - 1, 0),
        (num_tiles_x - 1, num_tiles_y - 1)
    ]

    iso_coords = [to_isometric(x, y, tile_width, tile_height) for x, y in corners]
    min_iso_x = min(coord[0] for coord in iso_coords) - MAP_PADDING
    max_iso_x = max(coord[0] for coord in iso_coords) + MAP_PADDING
    min_iso_y = min(coord[1] for coord in iso_coords) - MAP_PADDING
    max_iso_y = max(coord[1] for coord in iso_coords) + MAP_PADDING

    return min_iso_x, max_iso_x, min_iso_y, max_iso_y

def create_minimap_background(game_map, minimap_width, minimap_height):
    return
''' Needs to be modified
    """
    Crée la surface de la minimap représentant l'ensemble de la carte.
    """
    minimap_surface = pygame.Surface((minimap_width, minimap_height))
    minimap_surface.fill((0, 0, 0))

    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2

    num_tiles_x = game_map.num_tiles_x
    num_tiles_y = game_map.num_tiles_y

    iso_coords = [to_isometric(x, y, tile_width, tile_height) for x in [0, num_tiles_x - 1] for y in [0, num_tiles_y - 1]]
    iso_x_values = [coord[0] for coord in iso_coords]
    iso_y_values = [coord[1] for coord in iso_coords]
    min_iso_x = min(iso_x_values)
    max_iso_x = max(iso_x_values)
    min_iso_y = min(iso_y_values)
    max_iso_y = max(iso_y_values)

    iso_map_width = max_iso_x - min_iso_x
    iso_map_height = max_iso_y - min_iso_y

    scale = min(minimap_width / iso_map_width, minimap_height / iso_map_height)

    scaled_iso_map_width = iso_map_width * scale
    scaled_iso_map_height = iso_map_height * scale

    offset_x = (minimap_width - scaled_iso_map_width) / 2
    offset_y = (minimap_height - scaled_iso_map_height) / 2

    for y in range(num_tiles_y):
        for x in range(num_tiles_x):
            pos = (x, y)
            tile = game_map.grid.get(pos)
            terrain_type = tile.terrain_type if tile else 'grass'

            iso_x, iso_y = to_isometric(x, y, tile_width, tile_height)

            minimap_x = (iso_x - min_iso_x) * scale + offset_x
            minimap_y = (iso_y - min_iso_y) * scale + offset_y

            half_tile_width = (tile_width / 2) * scale
            half_tile_height = (tile_height / 2) * scale

            if terrain_type == 'gold':
                size_factor = 1.5
                half_tile_width *= size_factor
                half_tile_height *= size_factor

            points = [
                (minimap_x, minimap_y - half_tile_height),
                (minimap_x + half_tile_width, minimap_y),
                (minimap_x, minimap_y + half_tile_height),
                (minimap_x - half_tile_width, minimap_y)
            ]

            color = get_color_for_terrain(terrain_type)
            pygame.draw.polygon(minimap_surface, color, points)
    return minimap_surface, scale, offset_x, offset_y, min_iso_x, min_iso_y
'''
def draw_minimap(screen, minimap_background, camera, game_map, scale, offset_x, offset_y, min_iso_x, min_iso_y, minimap_rect):
    return
'''Needs to be modified 
    """
    Dessine la minimap à l'écran, avec le rectangle représentant la zone visible par le joueur.
    """
    screen.blit(minimap_background, minimap_rect.topleft)

    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2

    half_screen_width = camera.width / (2 * camera.zoom)
    half_screen_height = camera.height / (2 * camera.zoom)

    center_iso_x = -camera.offset_x
    center_iso_y = -camera.offset_y

    top_left_iso_x = center_iso_x - half_screen_width
    top_left_iso_y = center_iso_y - half_screen_height
    bottom_right_iso_x = center_iso_x + half_screen_width
    bottom_right_iso_y = center_iso_y + half_screen_height

    rect_left = (top_left_iso_x - min_iso_x) * scale + minimap_rect.x + offset_x
    rect_top = (top_left_iso_y - min_iso_y) * scale + minimap_rect.y + offset_y
    rect_right = (bottom_right_iso_x - min_iso_x) * scale + minimap_rect.x + offset_x
    rect_bottom = (bottom_right_iso_y - min_iso_y) * scale + minimap_rect.y + offset_y

    rect_x = rect_left
    rect_y = rect_top
    rect_width = rect_right - rect_left
    rect_height = rect_bottom - rect_top

    pygame.draw.rect(screen, (255, 255, 255), (rect_x, rect_y, rect_width, rect_height), 2)

    for pos, tile in game_map.grid.items():
        x, y = pos
        if tile.player is not None:
            iso_x, iso_y = to_isometric(x, y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2)
            minimap_x = (iso_x - min_iso_x) * scale + minimap_rect.x + offset_x
            minimap_y = (iso_y - min_iso_y) * scale + minimap_rect.y + offset_y

            half_tile_width = (HALF_TILE_SIZE / 2) * scale
            half_tile_height = (HALF_TILE_SIZE / 4) * scale

            points = [
                (minimap_x, minimap_y - half_tile_height),
                (minimap_x + half_tile_width, minimap_y),
                (minimap_x, minimap_y + half_tile_height),
                (minimap_x - half_tile_width, minimap_y)
            ]

            player_colors = [
                (255, 0, 0),
                (0, 0, 255),
            ]
            player_index = tile.player.nb - 1
            color = player_colors[player_index % len(player_colors)]

            pygame.draw.polygon(screen, (*color, 100), points)
'''
def display_fps(screen, clock):
    font = pygame.font.SysFont(None, 24)
    fps = int(clock.get_fps())
    fps_text = font.render(f'FPS: {fps}', True, pygame.Color('white'))
    screen.blit(fps_text, (10, 10))
