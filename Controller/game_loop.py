import time
import pygame
import sys
import random
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
from Controller.select_player import create_player_selection_surface, create_player_info_surface
from Settings.setup import MINIMAP_MARGIN, HALF_TILE_SIZE

def game_loop(screen, game_map, screen_width, screen_height, players):
    clock = pygame.time.Clock()
    camera = Camera(screen_width, screen_height)
    team_colors = generate_team_colors(len(players))
    min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_map)
    camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)

    minimap_margin = MINIMAP_MARGIN
    minimap_width = int(screen_width * 0.25)
    minimap_height = int(screen_height * 0.25)
    minimap_rect = pygame.Rect(
        screen_width - minimap_width - minimap_margin,
        screen_height - minimap_height - minimap_margin,
        minimap_width,
        minimap_height
    )

    minimap_background, minimap_scale, minimap_offset_x, minimap_offset_y, \
    minimap_min_iso_x, minimap_min_iso_y = create_minimap_background(
        game_map, minimap_width, minimap_height
    )

    minimap_entities_surface = pygame.Surface((minimap_width, minimap_height), pygame.SRCALPHA)
    minimap_entities_surface.fill((0,0,0,0))

    selected_player = players[0] if players else None
    minimap_dragging = False
    fullscreen = False

    game_state = {
        'camera': camera,
        'players': players,
        'selected_player': selected_player,
        'minimap_rect': minimap_rect,
        'minimap_dragging': minimap_dragging,
        'minimap_background': minimap_background,
        'minimap_scale': minimap_scale,
        'minimap_offset_x': minimap_offset_x,
        'minimap_offset_y': minimap_offset_y,
        'minimap_min_iso_x': minimap_min_iso_x,
        'minimap_min_iso_y': minimap_min_iso_y,
        'game_map': game_map,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'minimap_margin': minimap_margin,
        'screen': screen,
        'fullscreen': fullscreen,
        'player_selection_updated': True,
        'player_info_updated': True,
        'minimap_entities_surface': minimap_entities_surface,
        'team_colors': team_colors
    }

    player_selection_surface = None
    player_info_surface = None

    running = True
    update_interval = 60
    frame_counter = 0

    while running:
        dt = clock.tick(120) / 1000
        frame_counter += 1
        for event in pygame.event.get():
            handle_events(event, game_state)
            if event.type == pygame.QUIT:
                running = False

        update_game_state(game_state, dt)

        camera = game_state['camera']
        minimap_rect = game_state['minimap_rect']
        screen = game_state['screen']
        screen_width = game_state['screen_width']
        screen_height = game_state['screen_height']
        selected_player = game_state['selected_player']
        players = game_state['players']
        team_colors = game_state['team_colors']
        game_map = game_state['game_map']

        if game_state.get('recompute_camera', False):
            min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_state['game_map'])
            camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)
            game_state['recompute_camera'] = False

        if not game_state.get('paused', False):
            if frame_counter % update_interval == 0:
                update_minimap_entities(game_state)

            if game_state.get('player_selection_updated', False):
                player_selection_surface = create_player_selection_surface(
                    players, selected_player, minimap_rect, team_colors)
                game_state['player_selection_updated'] = False

            if game_state.get('player_info_updated', False):
                player_info_surface = create_player_info_surface(
                    selected_player, screen_width, team_colors)
                game_state['player_info_updated'] = False

        screen.fill((0, 0, 0))
        draw_map(screen, screen_width, screen_height, game_map, camera, players, team_colors)

        screen.blit(game_state['minimap_background'], minimap_rect.topleft)
        screen.blit(game_state['minimap_entities_surface'], minimap_rect.topleft)
        draw_minimap_viewport(screen, camera, minimap_rect,
                              game_state['minimap_scale'], 
                              game_state['minimap_offset_x'], 
                              game_state['minimap_offset_y'], 
                              game_state['minimap_min_iso_x'], 
                              game_state['minimap_min_iso_y'])

        if player_selection_surface:
            selection_surface_height = player_selection_surface.get_height()
            screen.blit(player_selection_surface, (minimap_rect.x, minimap_rect.y - selection_surface_height))

        if player_info_surface:
            info_surface_height = player_info_surface.get_height()
            screen.blit(player_info_surface, (0, screen_height - info_surface_height))

        display_fps(screen, clock)

        if game_state.get('force_full_redraw', False):
            pygame.display.flip()
            game_state['force_full_redraw'] = False
        else:
            pygame.display.flip()
