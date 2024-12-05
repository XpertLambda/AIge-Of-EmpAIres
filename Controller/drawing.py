# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/Projet_python\Controller\drawing.py

import pygame
import math
from Settings.setup import (
    HALF_TILE_SIZE,
    MINIMAP_MARGIN,
    MINIMAP_WIDTH,
    MINIMAP_HEIGHT,
    MAP_PADDING,
    TILE_SIZE
)
from Controller.isometric_utils import (
    to_isometric,
    get_color_for_terrain,
    screen_to_tile,
    tile_to_screen,
)
from Controller.init_sprites import draw_terrain, fill_grass, draw_building, draw_unit, draw_sprite
from Models.Map import Tile, GLOBAL_GRASS_TILE

tile_surfaces = {}  
building_surfaces = {}
iso_coords_cache = {}
prev_zoom = None
scaled_tile_cache = {}      
scaled_building_cache = {}

# Surfaces pré-calculées pour le terrain de base
base_surfaces = {
    'grass': None,
    'gold': None,
    'wood': None
}

def precompute_iso_coords(game_map):
    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2
    for y in range(game_map.num_tiles_y):
        for x in range(game_map.num_tiles_x):
            iso_x, iso_y = to_isometric(x, y, tile_width, tile_height)
            iso_coords_cache[(x, y)] = (iso_x, iso_y)

def create_base_surface(terrain_type):
    # Génère une surface de base pour un terrain donné
    surf_size = (int(TILE_SIZE), int(TILE_SIZE))
    surface = pygame.Surface(surf_size, pygame.SRCALPHA)
    surface.fill((0,0,0,0))

    class DummyCamera:
        def __init__(self, w, h):
            self.zoom = 1
            self.offset_x = 0
            self.offset_y = 0
            self.width = w
            self.height = h
    dummy_camera = DummyCamera(surf_size[0], surf_size[1])

    center_x = surf_size[0] // 2
    center_y = surf_size[1] // 2

    # Toujours remplir avec l'herbe
    fill_grass(surface, center_x, center_y, dummy_camera)
    if terrain_type == 'gold':
        draw_terrain('gold', surface, center_x, center_y, dummy_camera)
    elif terrain_type == 'wood':
        draw_terrain('wood', surface, center_x, center_y, dummy_camera)
    # food est non géré explicitement mais pourrait l'être similairement
    return surface

def ensure_base_surfaces():
    # Crée les surfaces de base si pas déjà fait
    if base_surfaces['grass'] is None:
        base_surfaces['grass'] = create_base_surface('grass')
    if base_surfaces['gold'] is None:
        base_surfaces['gold'] = create_base_surface('gold')
    if base_surfaces['wood'] is None:
        base_surfaces['wood'] = create_base_surface('wood')

def get_tile_surface(tile, pos):
    # Si c'est un tile herbe global, jamais dirty et identique, pas besoin de recalculer.
    if tile is GLOBAL_GRASS_TILE:
        # Juste retourner la base grass surface
        return base_surfaces['grass']

    # Sinon, on vérifie le cache
    if pos not in tile_surfaces or tile.dirty:
        # Génération surface spécifique
        surf_size = (int(TILE_SIZE), int(TILE_SIZE))
        surface = pygame.Surface(surf_size, pygame.SRCALPHA)
        surface.fill((0,0,0,0))

        class DummyCamera:
            def __init__(self, w, h):
                self.zoom = 1
                self.offset_x = 0
                self.offset_y = 0
                self.width = w
                self.height = h
        dummy_camera = DummyCamera(surf_size[0], surf_size[1])

        center_x = surf_size[0] // 2
        center_y = surf_size[1] // 2

        # On part toujours de la surface de base herbe
        surface.blit(base_surfaces['grass'], (0,0))

        if tile.building is None and tile.terrain_type != 'grass':
            # Ajouter la ressource
            if tile.terrain_type == 'gold':
                # On peut blit la surface gold par dessus la grass
                surface.blit(base_surfaces['gold'], (0,0))
            elif tile.terrain_type == 'wood':
                surface.blit(base_surfaces['wood'], (0,0))
            elif tile.terrain_type == 'food':
                # Pas pré-calculée, dessiner directement
                draw_terrain('food', surface, center_x, center_y, dummy_camera)

        tile_surfaces[pos] = surface
        tile.dirty = False
    return tile_surfaces[pos]

def render_building_surface(building, player):
    width_tiles = building.size1
    height_tiles = building.size2
    w = width_tiles * TILE_SIZE
    h = height_tiles * TILE_SIZE

    surface = pygame.Surface((w, h), pygame.SRCALPHA)
    surface.fill((0,0,0,0))

    class DummyCamera:
        def __init__(self, w, h):
            self.zoom = 1
            self.offset_x = 0
            self.offset_y = 0
            self.width = w
            self.height = h
    dummy_camera = DummyCamera(w, h)

    center_x = w // 2
    center_y = h // 2
    draw_building(building, surface, center_x, center_y, dummy_camera, player.nb if player else 0)

    return surface, (center_x, center_y)

def get_building_surface(building, player):
    b_id = id(building)
    if b_id not in building_surfaces:
        building_surfaces[b_id] = render_building_surface(building, player)
    return building_surfaces[b_id]

def draw_map(screen, screen_width, screen_height, game_map, camera, players):
    global prev_zoom
    zoom = camera.zoom

    if zoom != prev_zoom:
        scaled_tile_cache.clear()
        scaled_building_cache.clear()
        prev_zoom = zoom

    if not iso_coords_cache:
        precompute_iso_coords(game_map)
    ensure_base_surfaces()

    corners_screen = [
        (0, 0),
        (screen_width, 0),
        (0, screen_height),
        (screen_width, screen_height)
    ]

    tile_indices = [
        screen_to_tile(sx, sy, screen_width, screen_height, camera, HALF_TILE_SIZE / 2, HALF_TILE_SIZE / 4)
        for sx, sy in corners_screen
    ]

    x_indices = [tx for tx, _ in tile_indices]
    y_indices = [ty for _, ty in tile_indices]

    margin = 0

    min_tile_x = max(0, int(math.floor(min(x_indices))) - margin)
    max_tile_x = min(game_map.num_tiles_x - 1, int(math.ceil(max(x_indices))) + margin)
    min_tile_y = max(0, int(math.floor(min(y_indices))) - margin)
    max_tile_y = min(game_map.num_tiles_y - 1, int(math.ceil(max(y_indices))) + margin)

    buildings_to_draw = []

    # Dessin des tuiles
    for y in range(min_tile_y, max_tile_y + 1):
        for x in range(min_tile_x, max_tile_x + 1):
            tile = game_map.get_tile(x, y)
            tile_surface = get_tile_surface(tile, (x, y))

            iso_x, iso_y = iso_coords_cache[(x, y)]
            screen_x = (iso_x + camera.offset_x) * zoom + screen_width / 2
            screen_y = (iso_y + camera.offset_y) * zoom + screen_height / 2

            tile_key = ((x, y), zoom)
            if tile_key not in scaled_tile_cache:
                # Scale la tuile
                scaled_width = int(tile_surface.get_width() * zoom)
                scaled_height = int(tile_surface.get_height() * zoom)
                if scaled_width <= 0 or scaled_height <= 0:
                    continue
                scaled_surface = pygame.transform.scale(tile_surface, (scaled_width, scaled_height))
                scaled_tile_cache[tile_key] = scaled_surface
            else:
                scaled_surface = scaled_tile_cache[tile_key]

            screen.blit(scaled_surface, (screen_x - scaled_surface.get_width() // 2, screen_y - scaled_surface.get_height() // 2))

            if tile.building is not None and tile.building.x == x and tile.building.y == y:
                buildings_to_draw.append(tile.building)

    # Dessin des bâtiments
    for player in players:
        for building in player.buildings:
            if building in buildings_to_draw:
                building_surf, (bx_center, by_center) = get_building_surface(building, player)
                center_x = building.x + (building.size1 - 1) / 2
                center_y = building.y + (building.size2 - 1) / 2

                base_x = int(round(center_x))
                base_y = int(round(center_y))
                iso_x, iso_y = iso_coords_cache.get((base_x, base_y), (0,0))
                screen_x = (iso_x + camera.offset_x) * zoom + screen_width / 2
                screen_y = (iso_y + camera.offset_y) * zoom + screen_height / 2

                b_id = id(building)
                building_key = (b_id, zoom)
                if building_key not in scaled_building_cache:
                    scaled_b_w = int(building_surf.get_width() * zoom)
                    scaled_b_h = int(building_surf.get_height() * zoom)
                    if scaled_b_w <= 0 or scaled_b_h <= 0:
                        continue
                    scaled_building = pygame.transform.scale(building_surf, (scaled_b_w, scaled_b_h))
                    anchor_x = bx_center * zoom
                    anchor_y = by_center * zoom
                    scaled_building_cache[building_key] = (scaled_building, anchor_x, anchor_y)
                else:
                    scaled_building, anchor_x, anchor_y = scaled_building_cache[building_key]

                screen.blit(scaled_building, (screen_x - anchor_x, screen_y - anchor_y))

    # Dessin des unités (inchangé)
    for player in players:
        for unit in player.units:
            ux = int(round(unit.x))
            uy = int(round(unit.y))
            iso_x, iso_y = iso_coords_cache.get((ux, uy), (0,0))
            screen_x = (iso_x + camera.offset_x) * zoom + screen_width / 2
            screen_y = (iso_y + camera.offset_y) * zoom + screen_height / 2
            draw_unit(unit, screen, screen_x, screen_y, camera, team_number=player.nb)

def compute_map_bounds(game_map):
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
    if not iso_coords_cache:
        precompute_iso_coords(game_map)
    minimap_surface = pygame.Surface((minimap_width, minimap_height))
    minimap_surface.fill((0, 0, 0))

    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2

    num_tiles_x = game_map.num_tiles_x
    num_tiles_y = game_map.num_tiles_y

    iso_coords_corners = [to_isometric(x, y, tile_width, tile_height) for x in [0, num_tiles_x - 1] for y in [0, num_tiles_y - 1]]
    iso_x_values = [c[0] for c in iso_coords_corners]
    iso_y_values = [c[1] for c in iso_coords_corners]
    min_iso_x = min(iso_x_values)
    max_iso_x = max(iso_x_values)
    min_iso_y = min(iso_y_values)
    max_iso_y = max(iso_y_values)

    iso_map_width = max_iso_x - min_iso_x
    iso_map_height = max_iso_y - min_iso_y

    scale = min(minimap_width / iso_map_width, minimap_height / iso_map_height)
    offset_x = (minimap_width - iso_map_width * scale) / 2
    offset_y = (minimap_height - iso_map_height * scale) / 2

    # On peut se passer de dessin complexe si lent, mais on garde tel quel
    for y in range(num_tiles_y):
        for x in range(num_tiles_x):
            tile = game_map.grid.get((x,y))
            terrain_type = tile.terrain_type if tile else 'grass'

            iso_x, iso_y = iso_coords_cache[(x, y)]

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

def draw_minimap(screen, minimap_background, camera, game_map, scale, offset_x, offset_y, min_iso_x, min_iso_y, minimap_rect):
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
            iso_x, iso_y = iso_coords_cache[(x, y)]
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

            player_colors = [(255, 0, 0),(0, 0, 255)]
            player_index = tile.player.nb - 1
            color = player_colors[player_index % len(player_colors)]
            pygame.draw.polygon(screen, (*color, 100), points)

def display_fps(screen, clock):
    font = pygame.font.SysFont(None, 24)
    fps = int(clock.get_fps())
    fps_text = font.render(f'FPS: {fps}', True, pygame.Color('white'))
    screen.blit(fps_text, (10, 10))
