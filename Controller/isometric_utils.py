import math

def to_isometric(x, y, tile_width, tile_height):
    iso_x = (x - y) * (tile_width / 2)
    iso_y = (x + y) * (tile_height / 2)
    return iso_x, iso_y

def get_color_for_terrain(terrain_type):
    if terrain_type == 'gold':
        return (255, 215, 0)  
        
def screen_to_tile(sx, sy, screen_width, screen_height, camera, a, b):
    iso_x = (sx - screen_width / 2) / camera.zoom - camera.offset_x
    iso_y = (sy - screen_height / 2) / camera.zoom - camera.offset_y
    
    x = ((iso_x / a) + (iso_y / b)) / 2
    y = ((iso_y / b) - (iso_x / a)) / 2
    
    return int(x), int(y)

def tile_to_screen(x, y, width, height, camera, screen_width, screen_height):
    iso_x = (x - y) * (width / 2)
    iso_y = (x + y) * (height / 2)
    
    screen_x = (iso_x + camera.offset_x) * camera.zoom + screen_width / 2
    screen_y = (iso_y + camera.offset_y) * camera.zoom + screen_height / 2

    return screen_x, screen_y

def angle_with_x_axis(vx, vy):
    magnitude = math.sqrt(vx**2 + vy**2)
    cosine_theta = vx / magnitude
    theta_radians = math.acos(cosine_theta)
    theta_degrees = math.degrees(theta_radians)
    return theta_degrees