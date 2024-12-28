import time
import pygame
import sys
import random
from Models.Map import *
from Entity.Building import *
from Entity.Unit import *
from Models.Team import Team
from Controller.camera import Camera
from Controller.drawing import (
    draw_map,
    compute_map_bounds,
    create_minimap_background,
    display_fps,
    update_minimap_entities,
    draw_minimap_viewport,
    generate_team_colors
)
from Controller.event_handler import handle_events
from Controller.update import update_game_state
from Controller.gui import create_player_selection_surface, create_player_info_surface, get_scaled_gui, draw_gui_elements
from Settings.setup import HALF_TILE_SIZE, MINIMAP_MARGIN

PANEL_RATIO = 0.25
BG_RATIO    = 0.20

def get_centered_rect_in_bottom_right(width, height, screen_width, screen_height, margin=10):
    """
    Centre un rectangle (width x height) dans le coin inférieur droit de l'écran
    """
    rect = pygame.Rect(0, 0, width, height)
    center_x = screen_width - margin - (width // 2)
    center_y = screen_height - margin - (height // 2)
    rect.center = (center_x, center_y)
    return rect

def game_loop(screen, game_map, screen_width, screen_height, players):
    clock = pygame.time.Clock()
    camera = Camera(screen_width, screen_height)
    team_colors = generate_team_colors(len(players))

    min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_map)
    camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)

    panel_width  = int(screen_width * PANEL_RATIO)
    panel_height = int(screen_height * PANEL_RATIO)
    minimap_panel_sprite = get_scaled_gui('minimapPanel', 0, target_width=panel_width)
    minimap_panel_rect   = get_centered_rect_in_bottom_right(
        panel_width, panel_height, screen_width, screen_height, MINIMAP_MARGIN
    )

    bg_width  = int(screen_width * BG_RATIO)
    bg_height = int(screen_height * BG_RATIO)
    (minimap_background_surface,
     minimap_scale,
     minimap_offset_x,
     minimap_offset_y,
     minimap_min_iso_x,
     minimap_min_iso_y) = create_minimap_background(game_map, bg_width, bg_height)

    minimap_background_rect = minimap_background_surface.get_rect()
    minimap_background_rect.center = minimap_panel_rect.center
    minimap_background_rect.y -= panel_height / 50
    minimap_background_rect.x += panel_width / 18
    minimap_entities_surface = pygame.Surface(
        (minimap_background_rect.width, minimap_background_rect.height),
        pygame.SRCALPHA
    )
    minimap_entities_surface.fill((0, 0, 0, 0))

    selected_player = players[0] if players else None
    fullscreen = False

    game_state = {
        'camera': camera,
        'players': players,
        'selected_player': selected_player,
        'team_colors': team_colors,
        'game_map': game_map,
        'minimap_panel_sprite': minimap_panel_sprite,
        'minimap_panel_rect': minimap_panel_rect,
        'minimap_background': minimap_background_surface,
        'minimap_background_rect': minimap_background_rect,
        'minimap_entities_surface': minimap_entities_surface,
        'minimap_scale': minimap_scale,
        'minimap_offset_x': minimap_offset_x,
        'minimap_offset_y': minimap_offset_y,
        'minimap_min_iso_x': minimap_min_iso_x,
        'minimap_min_iso_y': minimap_min_iso_y,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'screen': screen,
        'fullscreen': fullscreen,
        'minimap_dragging': False,
        'player_selection_updated': True,
        'player_info_updated': True,
        'last_terminal_update': 0,
        'selecting_units': False,
        'selection_start': None,
        'selection_end': None,
        'selected_units': [],
        'show_all_health_bars': False,
        'minimap_margin': MINIMAP_MARGIN,
        'force_full_redraw': False
    }

    player_selection_surface = None
    player_info_surface = None

    running = True
    update_interval = 60
    frame_counter = 0
    elapsed_time = 0

    PLAYER_SELECTION_MARGIN = 20

    while running:
        dt = clock.tick(120) / 1000
        elapsed_time += dt
        frame_counter += 1

        for event in pygame.event.get():
            handle_events(event, game_state)
            if event.type == pygame.QUIT:
                running = False

        update_game_state(game_state, dt)

        camera = game_state['camera']
        screen = game_state['screen']
        screen_width = game_state['screen_width']
        screen_height = game_state['screen_height']
        selected_player = game_state['selected_player']
        players = game_state['players']
        team_colors = game_state['team_colors']
        game_map = game_state['game_map']

        if time.time() - game_state.get('last_terminal_update', 0) >= 2:
            start_time = time.time()
            game_map.update_terminal()
            game_state['last_terminal_update'] = start_time

        if game_state.get('recompute_camera', False):
            min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_map)
            camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)
            game_state['recompute_camera'] = False

        if not game_state.get('paused', False):
            if frame_counter % update_interval == 0:
                update_minimap_entities(game_state)

            if game_state.get('player_selection_updated', False):
                player_selection_surface = create_player_selection_surface(
                    players,
                    selected_player,
                    game_state['minimap_background_rect'],
                    team_colors
                )
                game_state['player_selection_updated'] = False

            if game_state.get('player_info_updated', False):
                player_info_surface = create_player_info_surface(
                    selected_player, screen_width, team_colors
                )
                game_state['player_info_updated'] = False

        screen.fill((0, 0, 0))
        draw_map(
            screen, screen_width, screen_height,
            game_map, camera, players, team_colors, game_state
        )

        screen.blit(game_state['minimap_panel_sprite'], game_state['minimap_panel_rect'].topleft)
        screen.blit(game_state['minimap_background'], game_state['minimap_background_rect'].topleft)
        screen.blit(game_state['minimap_entities_surface'], game_state['minimap_background_rect'].topleft)
        draw_minimap_viewport(
            screen,
            camera,
            game_state['minimap_background_rect'],
            game_state['minimap_scale'],
            game_state['minimap_offset_x'],
            game_state['minimap_offset_y'],
            game_state['minimap_min_iso_x'],
            game_state['minimap_min_iso_y']
        )

        draw_gui_elements(screen, screen_width, screen_height)

        if player_selection_surface:
            sel_h = player_selection_surface.get_height()
            bg_rect = game_state['minimap_background_rect']
            screen.blit(player_selection_surface, (bg_rect.x, bg_rect.y - sel_h - PLAYER_SELECTION_MARGIN))

        if player_info_surface:
            inf_h = player_info_surface.get_height()
            screen.blit(player_info_surface, (0, screen_height - inf_h))

        display_fps(screen, clock)

        if game_state.get('force_full_redraw', False):
            pygame.display.flip()
            game_state['force_full_redraw'] = False
        else:
            pygame.display.flip()

        barrack = Barracks(selected_player)
        if selected_player.resources["wood"] >= barrack.cost[2]:
            selected_player.buildBatiment(barrack, elapsed_time, 3, game_map)
        selected_player.manage_creation(elapsed_time)
