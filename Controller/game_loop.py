import time
import pygame
import sys
import random
from Models.Map import GameMap
from Entity.Building import *
from Entity.Unit import *
from Models.Team import Team
from Controller.camera import Camera
from Controller.terminal_display_debug import debug_print
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
from Controller.Bot import *
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

from Controller.Bot import manage_battle

def is_player_dead(player):
    # Simple check: no units, no buildings, and zero resources to rebuild
    if not player.units and not player.buildings:
        if (player.resources.food <= 50 and
            player.resources.gold <= 225):
            return True
    return False

def draw_game_over_overlay(screen, game_state):
    font = pygame.font.SysFont(None, 48)
    text = font.render(f"Joueur {game_state['winner_id']} est gagnant!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(game_state['screen_width'] // 2, game_state['screen_height'] // 2 - 50))
    screen.blit(text, text_rect)

    button_font = pygame.font.SysFont(None, 36)
    button_text = button_font.render("Quitter le jeu", True, (255, 255, 255))
    button_rect = button_text.get_rect(center=(game_state['screen_width'] // 2, game_state['screen_height'] // 2 + 50))
    pygame.draw.rect(screen, (0, 0, 0), button_rect.inflate(20, 10))
    screen.blit(button_text, button_rect)
    game_state['game_over_button_rect'] = button_rect

    # Nouveau bouton "Menu Principal"
    main_menu_text = button_font.render("Menu Principal", True, (255, 255, 255))
    main_menu_rect = main_menu_text.get_rect(
        center=(game_state['screen_width'] // 2, game_state['screen_height'] // 2 + 100)
    )
    pygame.draw.rect(screen, (0, 0, 0), main_menu_rect.inflate(20, 10))
    screen.blit(main_menu_text, main_menu_rect)
    game_state['main_menu_button_rect'] = main_menu_rect

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
        'show_gui_elements': True,
        'return_to_menu': False,  # Nouveau flag
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

    players_target=[None for _ in range(0,len(players))]
    selected_player.units.add(Swordsman(team=selected_player.teamID))
    priority_2(players,selected_player,players_target)
    while running:
        raw_dt = clock.tick(160) / ONE_SECOND
        dt = 0 if game_state['paused'] else raw_dt
        dt = dt * GAME_SPEED

        events = pygame.event.get()
        for event in events:
            handle_events(event, game_state)
            if event.type == pygame.QUIT:
                running = False
            if game_state.get('game_over', False):
                # On rend la souris visible pour cliquer sur les boutons
                pygame.mouse.set_visible(True)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    if 'game_over_button_rect' in game_state:
                        if game_state['game_over_button_rect'].collidepoint(mx, my):
                            user_choices["menu_result"] = "quit"
                            running = False
                    if 'main_menu_button_rect' in game_state:
                        if game_state['main_menu_button_rect'].collidepoint(mx, my):
                            user_choices["menu_result"] = "main_menu"
                            # Retour au menu
                            game_state['game_over'] = False
                            user_choices["validated"] = False
                            game_state['return_to_menu'] = True

        if game_state.get('return_to_menu'):
            # On sort de la boucle => retour menu
            break

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

        manage_battle(selected_player,players_target,players,game_map,dt)
        print("enemy unit")
        for unit in players_target[selected_player.teamID].units:
            print(unit.hp)
        print("-----")

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

        # Remove players who are dead
        for p in players[:]:
            if is_player_dead(p):
                debug_print(f"[GAME] Joueur {p.teamID} est éliminé.")
                players.remove(p)

        if len(players) == 1 and not game_state.get('game_over', False):
            debug_print(f"[GAME] Joueur {players[0].teamID} est gagnant.")
            game_state['winner_id'] = players[0].teamID
            game_state['game_over'] = True
            game_state['paused'] = True

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
            display_fps(screen, clock, font)
            if game_state.get('game_over', False):
                draw_game_over_overlay(screen, game_state)
            if game_state.get('force_full_redraw', False):
                pygame.display.flip()
                game_state['force_full_redraw'] = False
            else:
                pygame.display.flip()

    # fin de game_loop
