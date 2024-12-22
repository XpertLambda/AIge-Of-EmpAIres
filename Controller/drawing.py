import pygame
import math
import colorsys
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
from Controller.init_sprites import fill_grass
from Entity.Building import Building
from Entity.Resource.Gold import Gold

def generate_team_colors(nb_players):
    colors = []
    step = 1.0 / nb_players
    for i in range(nb_players):
        hue = (i * step) % 1.0
        if 0.25 <= hue <= 0.4167:
            hue = (hue + 0.2) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 0.7)
        colors.append((int(r*255), int(g*255), int(b*255)))
    return colors

def draw_health_bar(screen, screen_x, screen_y, entity, team_colors, game_state):
    # Si on veut forcer l'affichage pour tout le monde
    force_display = game_state.get('show_all_health_bars', False)

    # Vérifier si l’entité est un bâtiment ou une unité (sinon on ignore)
    if not (isinstance(entity, Building) or isinstance(entity, Unit)):
        return

    # Soit l’entité veut afficher sa barre (cliqué/endommagé/sélectionné),
    # soit on force l’affichage global
    display_condition = (
        entity.should_draw_health_bar()
        or (entity in game_state.get('selected_units', []))
        or force_display
    )
    if not display_condition:
        return

    ratio = entity.get_health_ratio()
    if ratio <= 0:
        return

    bar_width = 40
    bar_height = 5
    team_color = (255, 255, 255)
    if entity.team is not None:
        team_color = team_colors[entity.team % len(team_colors)]

    bg_rect = pygame.Rect(screen_x - bar_width//2, screen_y - 30, bar_width, bar_height)
    pygame.draw.rect(screen, (50,50,50), bg_rect)

    fill_width = int(bar_width * ratio)
    fill_rect = pygame.Rect(screen_x - bar_width//2, screen_y - 30, fill_width, bar_height)
    pygame.draw.rect(screen, team_color, fill_rect)

def draw_map(screen, screen_width, screen_height, game_map, camera, players, team_colors, game_state):
    corners_screen = [
        (0, 0),
        (screen_width, 0),
        (0, screen_height),
        (screen_width, screen_height)
    ]

    tile_indices = [
        screen_to_tile(sx, sy, screen_width, screen_height, camera,
                       HALF_TILE_SIZE / 2, HALF_TILE_SIZE / 4)
        for sx, sy in corners_screen
    ]

    x_indices = [tile_x for tile_x, _ in tile_indices]
    y_indices = [tile_y for _, tile_y in tile_indices]

    margin = 5

    min_tile_x = max(0, min(x_indices) - margin)
    max_tile_x = min(game_map.num_tiles_x - 1, max(x_indices) + margin)
    min_tile_y = max(0, min(y_indices) - margin)
    max_tile_y = min(game_map.num_tiles_y - 1, max(y_indices) + margin)
    visible_entites = set()

    for y in range(min_tile_y, max_tile_y):
        for x in range(min_tile_x, max_tile_x):
            # On dessine l'herbe ponctuellement (exemple)
            if x % 10 == 0 and y % 10 == 0:
                sx, sy = tile_to_screen(x+4.5, y+4.5,
                                        HALF_TILE_SIZE, HALF_TILE_SIZE / 2,
                                        camera, screen_width, screen_height)
                fill_grass(screen, sx, sy, camera)

            entities = game_map.grid.get((x, y), None)
            if entities:
                for entity in entities:
                    visible_entites.add(entity)

    for entity in sorted(visible_entites, key=lambda e: (e.y, e.x)):
        entity.display(screen, screen_width, screen_height, camera)
        sx, sy = tile_to_screen(entity.x, entity.y,
                                HALF_TILE_SIZE, HALF_TILE_SIZE / 2,
                                camera, screen_width, screen_height)
        draw_health_bar(screen, sx, sy, entity, team_colors, game_state)

    # Dessiner le rectangle de sélection si on est en train de sélectionner
    if game_state.get('selecting_units', False):
        sel_start = game_state.get('selection_start')
        sel_end = game_state.get('selection_end')
        if sel_start and sel_end:
            x1, y1 = sel_start
            x2, y2 = sel_end
            rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
            rect.normalize()
            pygame.draw.rect(screen, (255,255,255), rect, 1)

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
    minimap_surface = pygame.Surface((minimap_width, minimap_height))
    minimap_surface.fill((0, 0, 0))

    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2
    num_tiles_x = game_map.num_tiles_x
    num_tiles_y = game_map.num_tiles_y

    iso_coords = [
        to_isometric(0, 0, tile_width, tile_height),
        to_isometric(0, num_tiles_y - 1, tile_width, tile_height),
        to_isometric(num_tiles_x - 1, num_tiles_y - 1, tile_width, tile_height),
        to_isometric(num_tiles_x - 1, 0, tile_width, tile_height)
    ]

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

    points = []
    for iso_x, iso_y in iso_coords:
        mx = (iso_x - min_iso_x) * scale + offset_x
        my = (iso_y - min_iso_y) * scale + offset_y
        points.append((mx, my))
    pygame.draw.polygon(minimap_surface, (0, 128, 0), points)

    return minimap_surface, scale, offset_x, offset_y, min_iso_x, min_iso_y

def update_minimap_entities(game_state):
    camera = game_state['camera']
    game_map = game_state['game_map']
    team_colors = game_state['team_colors']
    minimap_scale = game_state['minimap_scale']
    minimap_offset_x = game_state['minimap_offset_x']
    minimap_offset_y = game_state['minimap_offset_y']
    minimap_min_iso_x = game_state['minimap_min_iso_x']
    minimap_min_iso_y = game_state['minimap_min_iso_y']
    minimap_entities_surface = game_state['minimap_entities_surface']

    minimap_entities_surface.fill((0,0,0,0))

    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2

    entities_to_draw = set()
    for pos, entities in game_map.grid.items():
        for e in entities:
            entities_to_draw.add(e)

    MIN_BUILDING_SIZE = 4
    MIN_UNIT_RADIUS = 3

    for entity in entities_to_draw:
        x, y = entity.x, entity.y
        team = entity.team
        size = entity.size
        iso_x, iso_y = to_isometric(x, y, tile_width, tile_height)
        mx = (iso_x - minimap_min_iso_x) * minimap_scale + minimap_offset_x
        my = (iso_y - minimap_min_iso_y) * minimap_scale + minimap_offset_y

        if team is not None:
            color = team_colors[team % len(team_colors)]
            if isinstance(entity, Building):
                half_dim = max(MIN_BUILDING_SIZE, size)
                rect = pygame.Rect(mx - half_dim, my - half_dim, half_dim*2, half_dim*2)
                pygame.draw.rect(minimap_entities_surface, (*color, 150), rect)
            else:
                radius = max(MIN_UNIT_RADIUS, size)
                pygame.draw.circle(minimap_entities_surface, (*color, 150), (mx, my), radius)
        elif isinstance(entity, Gold):
            color = get_color_for_terrain('gold')
            radius = max(MIN_UNIT_RADIUS, size)
            pygame.draw.circle(minimap_entities_surface, (*color, 150), (mx, my), radius)

def draw_minimap_viewport(screen, camera, minimap_rect, scale, offset_x, offset_y, min_iso_x, min_iso_y):
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

    rect_w = rect_right - rect_left
    rect_h = rect_bottom - rect_top
    pygame.draw.rect(screen, (255,255,255), (rect_left, rect_top, rect_w, rect_h), 2)

def display_fps(screen, clock):
    font = pygame.font.SysFont(None, 24)
    fps = int(clock.get_fps())
    fps_text = font.render(f'FPS: {fps}', True, pygame.Color('white'))
    screen.blit(fps_text, (10, 10))
