import pygame
import math
import colorsys
import time
from Settings.setup import (
    HALF_TILE_SIZE,
    MINIMAP_WIDTH,
    MINIMAP_HEIGHT,
    MAP_PADDING,
    HEALTH_BAR_WIDTH,
    HEALTH_BAR_HEIGHT,
    HEALTH_BAR_OFFSET_Y
)
from Controller.isometric_utils import (
    to_isometric,
    get_color_for_terrain,
    screen_to_tile,
    tile_to_screen,
)
from Controller.init_assets import fill_grass
from Controller.gui import get_scaled_gui

def generate_team_colors(nb_players):
    colors = []
    step = 1.0 / nb_players
    for i in range(nb_players):
        hue = (i * step) % 1.0
        # évite un vert trop proche
        if 0.25 <= hue <= 0.4167:
            hue = (hue + 0.2) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 0.7)
        colors.append((int(r*255), int(g*255), int(b*255)))
    return colors

def draw_map(
    screen,
    screen_width,
    screen_height,
    game_map,
    camera,
    players,
    team_colors,
    game_state,
    dt
):
    """Draws the map, entities, selection rectangle, and health bars."""
    corners_screen = [
        (0, 0),
        (screen_width, 0),
        (0, screen_height),
        (screen_width, screen_height)
    ]
    tile_indices = [
        screen_to_tile(
            sx, sy, 
            screen_width, screen_height, 
            camera,
            HALF_TILE_SIZE/2, HALF_TILE_SIZE/4
        )
        for sx, sy in corners_screen
    ]

    x_indices = [tx for tx, _ in tile_indices]
    y_indices = [ty for _, ty in tile_indices]

    margin = 5
    min_tile_x = max(0, min(x_indices) - margin)
    max_tile_x = min(game_map.num_tiles_x - 1, max(x_indices) + margin)
    min_tile_y = max(0, min(y_indices) - margin)
    max_tile_y = min(game_map.num_tiles_y - 1, max(y_indices) + margin)

    visible_entities = set()

    for y in range(min_tile_y, max_tile_y):
        for x in range(min_tile_x, max_tile_x):
            if x % 10 == 0 and y % 10 == 0:
                sx, sy = tile_to_screen(x+4.5, y+4.5,
                                        HALF_TILE_SIZE, HALF_TILE_SIZE/2,
                                        camera, screen_width, screen_height)
                fill_grass(screen, sx, sy, camera)

            entities = game_map.grid.get((x, y), None)
            inactive_entities = game_map.inactive_matrix.get((x, y), None)

            if entities:
                for entity in entities:
                    visible_entities.add(entity)
                    
            if inactive_entities:
                for entity in inactive_entities:
                    visible_entities.add(entity)

    visible_list = list(visible_entities)
    # Sort them by isometric layering
    visible_list.sort(key=lambda entity: (entity.y, entity.x))

    for e in visible_list:
        e.display_hitbox(screen, screen_width, screen_height, camera)
        e.display(screen, screen_width, screen_height, camera, dt)

    if game_state.get('selecting_entities', False):
        sel_start = game_state.get('selection_start')
        sel_end = game_state.get('selection_end')
        if sel_start and sel_end:
            x1, y1 = sel_start
            x2, y2 = sel_end
            rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
            rect.normalize()
            pygame.draw.rect(screen, (255,255,255), rect, 1)

    show_all = game_state.get('show_all_health_bars', False)

    if show_all:
        for e in visible_list:
            color = get_entity_bar_color(e, game_state, team_colors)
            e.display_healthbar(screen, screen_width, screen_height, camera, color=color)
    else:
        selected = game_state.get('selected_entities', [])
        for e in visible_list:
            if e in selected or (e.hp < e.max_hp):
                color = get_entity_bar_color(e, game_state, team_colors)
                e.display_healthbar(screen, screen_width, screen_height, camera, color=color)

def get_entity_bar_color(entity, game_state, team_colors):
    """
    Détermine la couleur de la barre de vie en fonction de l'équipe ou neutre.
    """
    if entity.team is None:
        return (50, 255, 50)  # vert pomme
    return team_colors[entity.team % len(team_colors)]

def compute_map_bounds(game_map):
    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2
    num_tiles_x = game_map.num_tiles_x
    num_tiles_y = game_map.num_tiles_y

    corners = [
        (0, 0),
        (0, num_tiles_y - 1),
        (num_tiles_x - 1, num_tiles_y - 1),
        (num_tiles_x - 1, 0)
    ]

    iso_coords = [to_isometric(x, y, tile_width, tile_height) for x, y in corners]
    min_iso_x = min(c[0] for c in iso_coords) - MAP_PADDING
    max_iso_x = max(c[0] for c in iso_coords) + MAP_PADDING
    min_iso_y = min(c[1] for c in iso_coords) - MAP_PADDING
    max_iso_y = max(c[1] for c in iso_coords) + MAP_PADDING

    return min_iso_x, max_iso_x, min_iso_y, max_iso_y

def create_minimap_background(game_map, minimap_width, minimap_height):
    minimap_surface = pygame.Surface((minimap_width, minimap_height), pygame.SRCALPHA)
    minimap_surface.fill((0, 0, 0, 0))

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

    iso_x_values = [ic[0] for ic in iso_coords]
    iso_y_values = [ic[1] for ic in iso_coords]
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
    for (ix, iy) in iso_coords:
        mx = (ix - min_iso_x) * scale + offset_x
        my = (iy - min_iso_y) * scale + offset_y
        points.append((mx, my))

    return minimap_surface, scale, offset_x, offset_y, min_iso_x, min_iso_y

def update_minimap_entities(game_state):
    from Entity.Building import Building
    from Entity.Resource.Gold import Gold
    camera = game_state['camera']
    game_map = game_state['game_map']
    team_colors = game_state['team_colors']
    minimap_scale = game_state['minimap_scale']
    minimap_offset_x = game_state['minimap_offset_x']
    minimap_offset_y = game_state['minimap_offset_y']
    minimap_min_iso_x = game_state['minimap_min_iso_x']
    minimap_min_iso_y = game_state['minimap_min_iso_y']
    minimap_entities_surface = game_state['minimap_entities_surface']

    minimap_entities_surface.fill((0, 0, 0, 0))

    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2

    entities_to_draw = set()
    for pos, ents in game_map.grid.items():
        for e in ents:
            entities_to_draw.add(e)

    MIN_BUILDING_SIZE = 3
    MIN_UNIT_RADIUS = 2

    for e in entities_to_draw:
        x, y = e.x, e.y
        iso_x, iso_y = to_isometric(x, y, tile_width, tile_height)
        mx = (iso_x - minimap_min_iso_x) * minimap_scale + minimap_offset_x
        my = (iso_y - minimap_min_iso_y) * minimap_offset_y + minimap_offset_y  # Typo? Usually it's * minimap_scale?
        my = (iso_y - minimap_min_iso_y) * minimap_scale + minimap_offset_y

        t_id = e.team
        if t_id is not None:
           
            color = team_colors[t_id % len(team_colors)]
            if isinstance(e, Building):
                half_dim = max(MIN_BUILDING_SIZE, e.size)
                r = pygame.Rect(mx - half_dim, my - half_dim, half_dim*2, half_dim*2)
                pygame.draw.rect(minimap_entities_surface, (*color, 150), r)
            else:
                radius = max(MIN_UNIT_RADIUS, e.size)
                pygame.draw.circle(minimap_entities_surface, (*color, 150), (mx, my), radius)
        else:
            if isinstance(e, Gold):
                color = get_color_for_terrain('gold')
                radius = max(MIN_UNIT_RADIUS, e.size)
                pygame.draw.circle(minimap_entities_surface, (*color, 150), (mx, my), radius)

def draw_minimap_viewport(screen, camera, minimap_rect, scale, offset_x, offset_y, min_iso_x, min_iso_y):
    half_screen_w = camera.width / (2 * camera.zoom)
    half_screen_h = camera.height / (2 * camera.zoom)

    center_iso_x = -camera.offset_x
    center_iso_y = -camera.offset_y
    left_iso_x = center_iso_x - half_screen_w
    left_iso_y = center_iso_y - half_screen_h
    right_iso_x = center_iso_x + half_screen_w
    right_iso_y = center_iso_y + half_screen_h

    rect_left = (left_iso_x - min_iso_x) * scale + minimap_rect.x + offset_x
    rect_top = (left_iso_y - min_iso_y) * scale + minimap_rect.y + offset_y
    rect_right = (right_iso_x - min_iso_x) * scale + minimap_rect.x + offset_x
    rect_bottom = (right_iso_y - min_iso_y) * scale + minimap_rect.y + offset_y

    rw = rect_right - rect_left
    rh = rect_bottom - rect_top
    pygame.draw.rect(screen, (255,255,255), (rect_left, rect_top, rw, rh), 2)

def display_fps(screen):
    if not hasattr(display_fps, "last_time"):
        display_fps.last_time = time.time()
        display_fps.frame_count = 0
        display_fps.fps = 0
    
    display_fps.frame_count += 1
    now = time.time()
    elapsed = now - display_fps.last_time
    if elapsed >= 1.0:
        display_fps.fps = display_fps.frame_count / elapsed
        display_fps.frame_count = 0
        display_fps.last_time = now

    font = pygame.font.SysFont(None, 24)
    fps_text = font.render(f'FPS: {int(display_fps.fps)}', True, pygame.Color('white'))
    screen.blit(fps_text, (10, 10))

def draw_pointer(screen):
    mx, my = pygame.mouse.get_pos()
    pointer = get_scaled_gui('pointer', 0, target_width=30)
    rect = pointer.get_rect(center=(mx, my))
    screen.blit(pointer, rect.topleft)

def draw_healthBar(screen, sx, sy, ratio, color):
    import pygame
    bg_rect = pygame.Rect(sx - HEALTH_BAR_WIDTH//2, sy - HEALTH_BAR_OFFSET_Y,
                          HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), bg_rect)
    fill_width = int(HEALTH_BAR_WIDTH * ratio)
    fill_rect = pygame.Rect(bg_rect.x, bg_rect.y, fill_width, HEALTH_BAR_HEIGHT)
    pygame.draw.rect(screen, color, fill_rect)
