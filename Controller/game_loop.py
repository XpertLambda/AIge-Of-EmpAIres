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

    # Ajout du champ show_all_health_bars
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
        'team_colors': team_colors,
        'last_terminal_update': 0,

        # Sélection rectangulaire
        'selecting_units': False,
        'selection_start': None,
        'selection_end': None,
        'selected_units': [],

        # Nouveau champ : toggle global barres de vie
        'show_all_health_bars': False
    }

    player_selection_surface = None
    player_info_surface = None

    running = True
    update_interval = 60
    frame_counter = 0
    time=0
    while running:
        dt = clock.tick(120) / 1000
        time+=dt
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
        
        # Updating terminal display
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
                    players, selected_player, minimap_rect, team_colors)
                game_state['player_selection_updated'] = False

            if game_state.get('player_info_updated', False):
                player_info_surface = create_player_info_surface(
                    selected_player, screen_width, team_colors)
                game_state['player_info_updated'] = False

        screen.fill((0, 0, 0))
        # On passe game_state pour l'affichage des barres
        draw_map(screen, screen_width, screen_height, game_map, camera, players, team_colors, game_state)

        screen.blit(game_state['minimap_background'], minimap_rect.topleft)
        screen.blit(game_state['minimap_entities_surface'], minimap_rect.topleft)
        draw_minimap_viewport(screen, camera, minimap_rect,
                              game_state['minimap_scale'],
                              game_state['minimap_offset_x'],
                              game_state['minimap_offset_y'],
                              game_state['minimap_min_iso_x'],
                              game_state['minimap_min_iso_y'])

        if player_selection_surface:
            sel_h = player_selection_surface.get_height()
            screen.blit(player_selection_surface, (minimap_rect.x, minimap_rect.y - sel_h))

        if player_info_surface:
            inf_h = player_info_surface.get_height()
            screen.blit(player_info_surface, (0, screen_height - inf_h))

        display_fps(screen, clock)
            
        if game_state.get('force_full_redraw', False):
            pygame.display.flip()
            game_state['force_full_redraw'] = False
        else:
            pygame.display.flip()
        barrack=Barracks(selected_player)
        if selected_player.resources["wood"] >= barrack.cost[2]:
            selected_player.buildBatiment(barrack,time,3,game_map)
            print(len(selected_player.buildings))
        selected_player.manage_creation(time)