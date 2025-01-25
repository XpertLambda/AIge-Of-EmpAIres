import pygame
import math
import colorsys
from Settings.setup import *
import pygame


def to_isometric(x, y, tile_width, tile_height):
    iso_x = (x - y) * (tile_width / 2)
    iso_y = (x + y) * (tile_height / 2)
    return iso_x, iso_y

def screen_to_2_5d(sx, sy, screen_width, screen_height, camera, tile_width, tile_height):
    iso_x = (sx - screen_width / 2) / camera.zoom - camera.offset_x
    iso_y = (sy - screen_height / 2) / camera.zoom - camera.offset_y
    x = ((2 * iso_x) / tile_width + (2 * iso_y) / tile_height) / 2
    y = ((2 * iso_y) / tile_height - (2 * iso_x) / tile_width) / 2
    return x, y
    
def screen_to_tile(sx, sy, screen_width, screen_height, camera, a, b):
    iso_x = (sx - screen_width / 2) / camera.zoom - camera.offset_x
    iso_y = (sy - screen_height / 2) / camera.zoom - camera.offset_y
    x = ((iso_x / a) + (iso_y / b)) / 2
    y = ((iso_y / b) - (iso_x / a)) / 2
    return round(x), round(y)

def tile_to_screen(x, y, tile_width, tile_height, camera, screen_width, screen_height, z=0):
    iso_x = (x - y) * (tile_width / 2)
    iso_y = (x + y) * (tile_height / 2)

    iso_y -= z * tile_height/2
    screen_x = (iso_x + camera.offset_x) * camera.zoom + screen_width / 2
    screen_y = (iso_y + camera.offset_y) * camera.zoom + screen_height / 2
    return screen_x, screen_y

def get_angle(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.degrees(math.atan2(dy, dx))
    return (angle + 360) % 360

def get_snapped_angle(start, end, ALLOWED_ANGLES=ALLOWED_ANGLES):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.degrees(math.atan2(dy, dx))
    angle = (angle + 360) % 360
    return min(ALLOWED_ANGLES, key=lambda x: abs(x - angle))

def get_direction(snapped_angle_rad):
    return ((snapped_angle_rad // 45) + 1) % 8

def normalize(v):
    magnitude = math.sqrt(sum(x**2 for x in v))
    return [x / magnitude for x in v] if magnitude else None

def get_centered_rect_in_bottom_right(width, height, screen_width, screen_height, margin=10):
    rect = pygame.Rect(0, 0, width, height)
    center_x = screen_width - margin - (width // 2)
    center_y = screen_height - margin - (height // 2)
    rect.center = (center_x, center_y)
    return rect

def get_color_for_terrain(terrain_type):
    if terrain_type == 'gold':
        return (255, 215, 0)

def generate_team_colors(num_players):
    color_list = []
    step = 1.0 / num_players
    for i in range(num_players):
        hue = (i * step) % 1.0
        if 0.25 <= hue <= 0.4167:
            hue = (hue + 0.2) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 0.7)
        color_list.append((int(r * 255), int(g * 255), int(b * 255)))
    return color_list

def compute_map_bounds(game_map):
    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2
    map_width = game_map.num_tiles_x
    map_height = game_map.num_tiles_y

    corners = [
        (0, 0),
        (0, map_height - 1),
        (map_width - 1, map_height - 1),
        (map_width - 1, 0)
    ]
    iso_coords = [
        to_isometric(x, y, tile_width, tile_height) 
        for (x, y) in corners
    ]

    min_iso_x = min(c[0] for c in iso_coords) - MAP_PADDING
    max_iso_x = max(c[0] for c in iso_coords) + MAP_PADDING
    min_iso_y = min(c[1] for c in iso_coords) - MAP_PADDING
    max_iso_y = max(c[1] for c in iso_coords) + MAP_PADDING

    return min_iso_x, max_iso_x, min_iso_y, max_iso_y

def get_entity_bar_color(entity, game_state, team_colors):
    if entity.team is None:
        return (50, 255, 50)
    return team_colors[entity.team % len(team_colors)]

def generate_team_colors(num_players):
    color_list = []
    step = 1.0 / num_players
    for i in range(num_players):
        hue = (i * step) % 1.0
        if 0.25 <= hue <= 0.4167:
            hue = (hue + 0.2) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 0.7)
        color_list.append((int(r * 255), int(g * 255), int(b * 255)))
    return color_list

def get_entity_bar_color(entity, game_state, team_colors):
    if entity.team is None:
        return (50, 255, 50)
    return team_colors[entity.team % len(team_colors)]
