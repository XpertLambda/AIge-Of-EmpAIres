import math
from Settings.setup import *

def to_isometric(x, y, tile_width, tile_height):
    iso_x = (x - y) * (tile_width / 2)
    iso_y = (x + y) * (tile_height / 2)
    return iso_x, iso_y

def get_color_for_terrain(terrain_type):
    if terrain_type == 'gold':
        return (255, 215, 0)  

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

def tile_to_screen(x, y, width, height, camera, screen_width, screen_height):
    iso_x = (x - y) * (width / 2)
    iso_y = (x + y) * (height / 2)
    
    screen_x = (iso_x + camera.offset_x) * camera.zoom + screen_width / 2
    screen_y = (iso_y + camera.offset_y) * camera.zoom + screen_height / 2

    return screen_x, screen_y

def get_angle(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.degrees(math.atan2(dy, dx))
    angle = (angle + 360) % 360
    return angle

def get_snapped_angle(start, end, ALLOWED_ANGLES=ALLOWED_ANGLES):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.degrees(math.atan2(dy, dx))
    angle = (angle + 360) % 360
    snapped_angle = min(ALLOWED_ANGLES, key=lambda x: abs(x - angle))
    return snapped_angle

def get_direction(snapped_angle_rad):
    direction = ((snapped_angle_rad // 45 )+1)%8 
    return direction 
    # +1 to match the sprite sheet and %8 because tere are 8 directions

def normalize(v):
    magnitude = math.sqrt(sum(x**2 for x in v))
    if magnitude != 0:
        return [x / magnitude for x in v]
    return None