import pygame
import math
import colorsys
import time
from Settings.setup import (
    HALF_TILE_SIZE,
    MAP_PADDING,
    HEALTH_BAR_WIDTH,
    HEALTH_BAR_HEIGHT,
    HEALTH_BAR_OFFSET_Y,
    UNIT_HITBOX
)
from Controller.utils import *
from Controller.init_assets import *
from Controller.gui import get_scaled_gui

def draw_map(screen, screen_width, screen_height, game_map, camera, players, team_colors, game_state, delta_time):
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
            HALF_TILE_SIZE / 2,
            HALF_TILE_SIZE / 4
        )
        for sx, sy in corners_screen
    ]

    x_candidates = [t[0] for t in tile_indices]
    y_candidates = [t[1] for t in tile_indices]

    margin = 5
    min_tile_x = max(0, min(x_candidates) - margin)
    max_tile_x = min(game_map.num_tiles_x - 1, max(x_candidates) + margin)
    min_tile_y = max(0, min(y_candidates) - margin)
    max_tile_y = min(game_map.num_tiles_y - 1, max(y_candidates) + margin)

    visible_entities = set()
    visible_projectiles = set()

    # Entities: Iterate through visible tiles and add entities from those tiles
    for tile_y in range(min_tile_y, max_tile_y + 1):  # +1 to include max range
        for tile_x in range(min_tile_x, max_tile_x + 1):  # +1 to include max range
            entity_set_active = game_map.grid.get((tile_x, tile_y), None)
            entity_set_inactive = game_map.inactive_matrix.get((tile_x, tile_y), None)

            if entity_set_active:
                visible_entities.update(entity_set_active)  # Use update for efficiency
            if entity_set_inactive:
                visible_entities.update(entity_set_inactive)  # Use update for efficiency

    # Projectiles: Filter projectiles based on their tile position
    for projectile in game_map.projectiles.values():
        projx, projy = round(projectile.x), round(projectile.y)
        if min_tile_x <= projx <= max_tile_x and min_tile_y <= projy <= max_tile_y:  # Check if projectile tile is visible
            visible_projectiles.add(projectile)


    for tile_y in range(min_tile_y, max_tile_y):
        for tile_x in range(min_tile_x, max_tile_x):
            # Fill grass
            if tile_x % 10 == 0 and tile_y % 10 == 0:
                grass_sx, grass_sy = tile_to_screen(
                    tile_x + 4.5,
                    tile_y + 4.5,
                    HALF_TILE_SIZE,
                    HALF_TILE_SIZE / 2,
                    camera,
                    screen_width,
                    screen_height
                )
                fill_grass(screen, grass_sx, grass_sy, camera)


    visible_list = list(visible_entities)
    visible_list.sort(key=lambda e: (e.x + e.y))

    game_state['train_button_rects'] = {}
    current_time = time.time()

    # Draw entities
    for entity in visible_list:
        entity.display_hitbox(screen, screen_width, screen_height, camera)
        entity.display(screen, screen_width, screen_height, camera, delta_time)
        entity.display_range(screen, screen_width, screen_height, camera)
        if hasattr(entity, 'spawnsUnits') and entity.spawnsUnits:
            ent_screen_x, ent_screen_y = tile_to_screen(
                entity.x,
                entity.y,
                HALF_TILE_SIZE,
                HALF_TILE_SIZE / 2,
                camera,
                screen_width,
                screen_height
            )

            # Always show training progress if there's an active training
            if entity.current_training_unit:
                bar_width = 80
                bar_height = 6
                button_width = 120
                offset_y = 12 * entity.size
                button_x = int(ent_screen_x - button_width / 2)
                button_y = int(ent_screen_y - offset_y - 10)
                bar_x = button_x
                bar_y = button_y - 10

                # Draw progress bar
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                fill_w = int(bar_width * entity.training_progress)
                pygame.draw.rect(screen, (0, 220, 0), (bar_x, bar_y, fill_w, bar_height))

                # Draw queue length
                font_obj = pygame.font.Font(None, 18)
                queue_len = len(entity.training_queue)
                queue_text = f"Q:{queue_len}"
                queue_surf = font_obj.render(queue_text, True, (255, 255, 255))
                screen.blit(queue_surf, (bar_x + bar_width + 5, bar_y - 2))

            # Only show training button and feedback when selected
            if 'selected_entities' in game_state and entity in game_state['selected_entities']:
                button_width = 120
                button_height = 25
                ent_screen_x, ent_screen_y = tile_to_screen(
                    entity.x,
                    entity.y,
                    HALF_TILE_SIZE,
                    HALF_TILE_SIZE / 2,
                    camera,
                    screen_width,
                    screen_height
                )
                offset_y = 12 * entity.size
                button_x = int(ent_screen_x - button_width / 2)
                button_y = int(ent_screen_y - offset_y - 10)

                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                pygame.draw.rect(screen, (120, 120, 180), button_rect)
                font_obj = pygame.font.Font(None, 18)

                from Entity.Building.Building import UNIT_TRAINING_MAP
                if entity.acronym in UNIT_TRAINING_MAP:
                    unit_key = UNIT_TRAINING_MAP[entity.acronym]
                    button_text = f"Train {unit_key.capitalize()}"
                else:
                    button_text = "Train ???"

                text_surf = font_obj.render(button_text, True, (255, 255, 255))
                screen.blit(text_surf, text_surf.get_rect(center=button_rect.center))

                game_state['train_button_rects'][entity.entity_id] = button_rect

                # If not enough resources feedback
                if 'insufficient_resources_feedback' in game_state:
                    if entity.entity_id in game_state['insufficient_resources_feedback']:
                        start_time = game_state['insufficient_resources_feedback'][entity.entity_id][0]
                        if current_time - start_time < 3:
                            warn_text = game_state['insufficient_resources_feedback'][entity.entity_id][1]
                            warn_surf = font_obj.render(warn_text, True, (255, 50, 50))
                            screen.blit(warn_surf, (button_x, button_y - 22))
                        else:
                            game_state['insufficient_resources_feedback'].pop(entity.entity_id, None)

    for projectile in visible_projectiles:
        projectile.display(screen, screen_width, screen_height, camera, delta_time)


    # Draw selection rectangle if needed
    if game_state.get('selecting_entities', False):
        start_pos = game_state.get('selection_start')
        end_pos = game_state.get('selection_end')
        if start_pos and end_pos:
            x1, y1 = start_pos
            x2, y2 = end_pos
            selection_rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
            selection_rect.normalize()
            pygame.draw.rect(screen, (255, 255, 255), selection_rect, 1)

    # Health bars
    show_all_bars = game_state.get('show_all_health_bars', False)
    show_unit_and_building = game_state.get('show_unit_and_building_health_bars', False)

    if show_all_bars:
        for entity in visible_list:
            color_val = get_entity_bar_color(entity, game_state, team_colors)
            entity.display_healthbar(screen, screen_width, screen_height, camera, color_val)
    elif show_unit_and_building:
        from Entity.Unit.Unit import Unit
        from Entity.Building import Building
        for entity in visible_list:
            if isinstance(entity, Unit) or isinstance(entity, Building):
                color_val = get_entity_bar_color(entity, game_state, team_colors)
                entity.display_healthbar(screen, screen_width, screen_height, camera, color_val)
    else:
        selected_entities = game_state.get('selected_entities', [])
        for entity in visible_list:
            if entity in selected_entities or entity.hp < entity.max_hp:
                color_val = get_entity_bar_color(entity, game_state, team_colors)
                entity.display_healthbar(screen, screen_width, screen_height, camera, color_val)

def create_minimap_background(game_map, minimap_width, minimap_height):
    surface_map = pygame.Surface((minimap_width, minimap_height), pygame.SRCALPHA)
    surface_map.fill((0, 0, 0, 0))

    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2
    nx = game_map.num_tiles_x
    ny = game_map.num_tiles_y

    corner_coords = [
        to_isometric(0, 0, tile_width, tile_height),
        to_isometric(0, ny - 1, tile_width, tile_height),
        to_isometric(nx - 1, ny - 1, tile_width, tile_height),
        to_isometric(nx - 1, 0, tile_width, tile_height)
    ]
    iso_xs = [c[0] for c in corner_coords]
    iso_ys = [c[1] for c in corner_coords]
    min_iso_x = min(iso_xs)
    max_iso_x = max(iso_xs)
    min_iso_y = min(iso_ys)
    max_iso_y = max(iso_ys)

    iso_map_width = max_iso_x - min_iso_x
    iso_map_height = max_iso_y - min_iso_y
    scale_factor = min(minimap_width / iso_map_width, minimap_height / iso_map_height)
    scaled_width = iso_map_width * scale_factor
    scaled_height = iso_map_height * scale_factor
    offset_x = (minimap_width - scaled_width) / 2
    offset_y = (minimap_height - scaled_height) / 2

    return surface_map, scale_factor, offset_x, offset_y, min_iso_x, min_iso_y

def display_fps(screen, screen_width, clock, font):
    fps_value = f"FPS {int(clock.get_fps())}"
    fps_surface = font.render(fps_value, True, (255, 255, 255))  # White text
    screen.blit(fps_surface, (screen_width - 70, 10))  # (x, y) coordinates for top-left

def draw_pointer(screen):
    from Controller.gui import get_scaled_gui  # Déplacé ici pour éviter l'import circulaire
    mouse_x, mouse_y = pygame.mouse.get_pos()
    pointer_image = get_scaled_gui('pointer', 0, target_width=30)
    pointer_rect = pointer_image.get_rect(center=(mouse_x + pointer_image.get_width() //2, mouse_y + pointer_image.get_height() //2))
    screen.blit(pointer_image, pointer_rect.topleft)

def draw_healthBar(screen, screen_x, screen_y, ratio, color_val):
    bg_rect = pygame.Rect(
        screen_x - HEALTH_BAR_WIDTH // 2,
        screen_y - HEALTH_BAR_OFFSET_Y,
        HEALTH_BAR_WIDTH,
        HEALTH_BAR_HEIGHT
    )
    pygame.draw.rect(screen, (50, 50, 50), bg_rect)
    fill_width = int(HEALTH_BAR_WIDTH * ratio)
    fill_rect = pygame.Rect(bg_rect.x, bg_rect.y, fill_width, HEALTH_BAR_HEIGHT)
    pygame.draw.rect(screen, color_val, fill_rect)

def draw_buildProcess(screen, screen_x, screen_y, time, zoom, color=(255,255,255)):
    minutes = time // 60
    seconds = time % 60
    time_text = f"{int(minutes)}:{int(seconds)}"
    base_font_size = 36
    font_size = int(base_font_size * zoom) 
    font = pygame.font.Font(None, font_size)
    time_surface = font.render(time_text, True, color)
    screen.blit(time_surface, (screen_x - time_surface.get_width()//2, screen_y - time_surface.get_height()//2))

def draw_hitbox(screen, corners, zoom, color):
    if len(corners) != 4:
        raise ValueError("Hitbox must have exactly 4 corners.")
    scaled_corners = [(x * zoom, y * zoom) for x, y in corners]
    pygame.draw.polygon(screen, color, corners, width=1)

def draw_path(screen, unit_center, screenPath, zoom, color):
    if len(screenPath) >= 2:
        pygame.draw.lines(screen, color, False, screenPath, max(1, int(4 * zoom)))
    pygame.draw.circle(screen, color, unit_center, int(5 * zoom))

def draw_sprite(screen, acronym, category, screen_x, screen_y, zoom, state=None, frame=0, variant=0, direction=0):
    name = Acronym[category][acronym]
    scaled_sprite = get_scaled_sprite(name, category, zoom, state, direction, frame, variant)
    if scaled_sprite is None:
        return
    scaled_width = scaled_sprite.get_width()
    scaled_height = scaled_sprite.get_height()
    screen.blit(scaled_sprite, (screen_x - scaled_width // 2, screen_y - scaled_height // 2))


def draw_gui_elements(screen, screen_width, screen_height):
    """
    Dessine le panneau de ressources (en haut) et autres éléments.
    """
    resources_panel_img = get_scaled_gui('ResourcesPanel', 0, target_width=screen_width // 2)
    screen.blit(resources_panel_img, (0, 0))

    pw, ph = resources_panel_img.get_width(), resources_panel_img.get_height()
    icon_scale_width = pw // 22

    # On place 3 icônes (gold, wood, food) alignées, petit offset vertical
    gold_img = get_scaled_gui('gold', 0, target_width=icon_scale_width)
    gold_x = 12
    screen.blit(gold_img, (gold_x, ph // 15))

    wood_img = get_scaled_gui('wood', 0, target_width=icon_scale_width)
    wood_x = gold_x + gold_img.get_width() + (2 * gold_img.get_width())
    screen.blit(wood_img, (wood_x, ph // 15))

    food_img = get_scaled_gui('food', 0, target_width=icon_scale_width)
    food_x = wood_x + wood_img.get_width() + (2 * wood_img.get_width())
    screen.blit(food_img, (food_x, ph // 15))

    # Minimap panel
    panel_width = int(screen_width * PANEL_RATIO)
    panel_height = int(screen_height * PANEL_RATIO)
    minimap_panel_sprite = get_scaled_gui('minimapPanel', 0, target_width=panel_width)
    minimap_panel_rect = get_centered_rect_in_bottom_right(
        panel_width, panel_height, screen_width, screen_height, MINIMAP_MARGIN
    )

    screen.blit(minimap_panel_sprite, minimap_panel_rect.topleft)


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

    rect_width = rect_right - rect_left
    rect_height = rect_bottom - rect_top

    pygame.draw.rect(
        screen, 
        (255, 255, 255), 
        (rect_left, rect_top, rect_width, rect_height), 
        2
    )

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

    rect_width = rect_right - rect_left
    rect_height = rect_bottom - rect_top

    pygame.draw.rect(
        screen, 
        (255, 255, 255), 
        (rect_left, rect_top, rect_width, rect_height), 
        2
    )

def fill_grass(screen, screen_x, screen_y, camera):
    draw_sprite(screen, ' ', 'resources', screen_x, screen_y, camera.zoom)