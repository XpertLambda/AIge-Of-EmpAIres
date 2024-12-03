# Controller/isometric_utils.py

def to_isometric(x, y, tile_width, tile_height):
    """
    Convertit les coordonnées cartésiennes en coordonnées isométriques.
    """
    iso_x = (x - y) * (tile_width / 2)
    iso_y = (x + y) * (tile_height / 2)
    return iso_x, iso_y

def get_color_for_terrain(terrain_type):
    """
    Retourne la couleur associée à un type de terrain.
    """
    if terrain_type == 'gold':
        return (255, 215, 0)  # Couleur pour 'gold'
    else:
        return (34, 139, 34)  # Couleur de l'herbe pour tous les autres terrains

def screen_to_tile(sx, sy, screen_width, screen_height, camera, a, b):
    # Convertit les coordonnées de l'écran en coordonnées isométriques
    iso_x = (sx - screen_width / 2) / camera.zoom - camera.offset_x
    iso_y = (sy - screen_height / 2) / camera.zoom - camera.offset_y
    
    # Convertit les coordonnées isométriques en indices de tuiles
    x = ((iso_x / a) + (iso_y / b)) / 2
    y = ((iso_y / b) - (iso_x / a)) / 2
    
    return x, y

def tile_to_screen(x, y, width, height, camera, screen_width, screen_height):
    # Convertit les coordonnées cartésiennes en coordonnées isométriques
    iso_x = (x - y) * (width / 2)
    iso_y = (x + y) * (height / 2)
    
    # Convertit les coordonnées isométriques en coordonnées d'écran avec ajustements de la caméra
    screen_x = (iso_x + camera.offset_x) * camera.zoom + screen_width / 2
    screen_y = (iso_y + camera.offset_y) * camera.zoom + screen_height / 2

    return screen_x, screen_y
