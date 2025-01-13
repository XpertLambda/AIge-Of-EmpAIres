import time
import pygame
import sys
import random
from Models.Map import GameMap
from Entity.Building import *
from Entity.Unit import *
from Models.Team import Team
from Controller.camera import Camera
from Controller.drawing import (
    draw_map,
    compute_map_bounds,
    create_minimap_background,
    display_fps,
    generate_team_colors,
    draw_pointer,
    draw_gui_elements,
    draw_minimap_viewport
)
import copy
from Controller.event_handler import handle_events
from Controller.update import update_game_state
from Controller.gui import (
    create_player_selection_surface,
    create_player_info_surface,
    get_scaled_gui,
    get_centered_rect_in_bottom_right,
    update_minimap_elements,
)
from Controller.utils import tile_to_screen
from Settings.setup import (
    HALF_TILE_SIZE,
    MINIMAP_MARGIN,
    UPDATE_EVERY_N_MILLISECOND,
    user_choices,
    GAME_SPEED,
    PANEL_RATIO,
    BG_RATIO,
    ONE_SECOND,
    FPS_DRAW_LIMITER
)

def game_loop(screen, game_map, screen_width, screen_height, players):
    clock = pygame.time.Clock()
    pygame.key.set_repeat(0, 0)
    camera = Camera(screen_width, screen_height)
    team_colors = generate_team_colors(len(players))
    pygame.mouse.set_visible(False)
    font = pygame.font.SysFont(None, 24)

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
    (
        minimap_background_surface,
        minimap_scale,
        minimap_offset_x,
        minimap_offset_y,
        minimap_min_iso_x,
        minimap_min_iso_y
    ) = create_minimap_background(game_map, bg_width, bg_height)

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
        'selected_entities': [],
        'selecting_entities': False,
        'selection_start': None,
        'selection_end': None,
        'rectangle_additive': False,
        'paused': False,
        'force_full_redraw': False,
        'show_all_health_bars': False,
        'show_player_info': True,
        'show_gui_elements': True,  # Nouveau flag pour F1
    }
    
    game_map.set_game_state(game_state)

    player_selection_surface = None
    player_info_surface = None

    running = True
    update_counter = 0

    old_resources = {}
    for p in players:
        old_resources[p.teamID] = p.resources.copy()

    draw_timer = 0
    while running:
        raw_dt = clock.tick(160) / ONE_SECOND
        dt = 0 if game_state['paused'] else raw_dt
        dt = dt * GAME_SPEED

        events = pygame.event.get()
        for event in events:
            handle_events(event, game_state)
            if event.type == pygame.QUIT:
                running = False

        screen = game_state['screen']
        screen_width = game_state['screen_width']
        screen_height = game_state['screen_height']
        selected_player = game_state['selected_player']
        players = game_state['players']
        team_colors = game_state['team_colors']
        game_map = game_state['game_map']
        camera = game_state['camera']

        # Terminal only => pas d'affichage Pygame
        if user_choices["index_terminal_display"] == 1:
            screen = None

        # Mise à jour (logique)
        if not game_state.get('paused', False):
            if update_counter > 1:
                update_counter = 0
                update_minimap_elements(game_state)
            update_counter += dt

        # Surfaces
        if not game_state.get('paused', False):
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

        update_game_state(game_state, dt)

        if selected_player is not None:
            current_res = selected_player.resources
            previous_res = old_resources[selected_player.teamID]
            if current_res != previous_res:
                game_state['player_info_updated'] = True
                old_resources[selected_player.teamID] = current_res.copy()

        # Rendu Pygame (GUI)
        draw_timer += raw_dt

        if screen is not None and draw_timer >= 1/FPS_DRAW_LIMITER:
            draw_timer = 0
            screen.fill((0, 0, 0))
            draw_map(
                screen,
                screen_width,
                screen_height,
                game_map,
                camera,
                players,
                team_colors,
                game_state,
                dt
            )
            
            if game_state['show_gui_elements']:
                draw_gui_elements(screen, screen_width, screen_height)
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

                if player_selection_surface:
                    sel_h = player_selection_surface.get_height()
                    bg_rect = game_state['minimap_background_rect']
                    screen.blit(player_selection_surface, (bg_rect.x, bg_rect.y - sel_h - 20))

                if player_info_surface and game_state['show_player_info']:
                    inf_h = player_info_surface.get_height()
                    screen.blit(player_info_surface, (0, screen_height - inf_h))

            draw_pointer(screen)

            for pl in game_map.players:
                for unit in pl.units:
                    if unit.path:
                        unit.display_path(
                            game_state['screen'],
                            game_state['screen_width'],
                            game_state['screen_height'],
                            game_state['camera']
                        )
            display_fps(screen, screen_width, clock, font)
            if game_state.get('force_full_redraw', False):
                pygame.display.flip()
                game_state['force_full_redraw'] = False
            else:
                pygame.display.flip()

    # fin de game_loop
