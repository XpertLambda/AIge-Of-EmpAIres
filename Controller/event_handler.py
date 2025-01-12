import pygame
import sys
import os
import time
from tkinter import Tk, filedialog
from Entity.Building import Building, TownCentre
from Controller.utils import *
from Settings.setup import HALF_TILE_SIZE, SAVE_DIRECTORY
from Controller.drawing import compute_map_bounds, generate_team_colors
from Models.html import write_full_html
from AiUtils.aStar import a_star
from Entity.Unit.Unit import Unit

def handle_events(event, game_state):
    camera = game_state['camera']
    players = game_state['players']
    selected_player = game_state['selected_player']
    screen_width = game_state['screen_width']
    screen_height = game_state['screen_height']

    if event.type == pygame.QUIT:
        try:
            os.remove('full_snapshot.html')
        except:
            pass
        pygame.quit()
        sys.exit()

    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F2:
            game_state['show_all_health_bars'] = not game_state['show_all_health_bars']
        elif event.key == pygame.K_F11:
            game_state['game_map'].save_map()
        elif event.key == pygame.K_F12:
            try:
                root = Tk()
                root.withdraw()
                chosen_path = filedialog.askopenfilename(
                    initialdir=SAVE_DIRECTORY,
                    filetypes=[("Pickle","*.pkl")]
                )
                root.destroy()
                if chosen_path:
                    from Controller.drawing import create_minimap_background, compute_map_bounds, generate_team_colors
                    from Models.Map import GameMap
                    game_state['game_map'] = GameMap(0, False, [], generate=False)
                    game_state['game_map'].load_map(chosen_path)
                    game_state['players'].clear()
                    game_state['players'].extend(game_state['game_map'].players)
                    if game_state['players']:
                        game_state['selected_player'] = game_state['players'][0]
                    else:
                        game_state['selected_player'] = None

                    game_state['team_colors'] = generate_team_colors(len(game_state['players']))
                    camera.offset_x = 0
                    camera.offset_y = 0
                    camera.zoom = 1.0
                    min_x, max_x, min_y, max_y = compute_map_bounds(game_state['game_map'])
                    camera.set_bounds(min_x, max_x, min_y, max_y)
                    game_state['force_full_redraw'] = True
            except Exception as e:
                print(f"Error loading: {e}")

        elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
            camera.set_zoom(camera.zoom * 1.1)
        elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            camera.set_zoom(camera.zoom / 1.1)
        elif event.key == pygame.K_m:
            camera.zoom_out_to_global()
        elif event.key == pygame.K_ESCAPE:
            try:
                os.remove('full_snapshot.html')
            except:
                pass
            pygame.quit()
            sys.exit()

    elif event.type == pygame.KEYUP:
        if event.key == pygame.K_TAB:
            game_state['paused'] = not game_state.get('paused', False)
            if game_state['paused']:
                write_full_html(game_state['players'], game_state['game_map'])

    elif event.type == pygame.MOUSEBUTTONDOWN:
        mouse_x, mouse_y = event.pos
        mods = pygame.key.get_mods()
        ctrl_pressed = (mods & pygame.KMOD_CTRL)

        if event.button == 1:
            if game_state['minimap_background_rect'].collidepoint(mouse_x, mouse_y):
                game_state['minimap_dragging'] = True
            else:
                train_rects = game_state.get('train_button_rects', {})
                clicked_building_id = None
                for bld_id, rect in train_rects.items():
                    if rect.collidepoint(mouse_x, mouse_y):
                        clicked_building_id = bld_id
                        break

                if clicked_building_id is not None:
                    building_clicked = find_entity_by_id(game_state, clicked_building_id)
                    if building_clicked and selected_player:
                        if building_clicked.team == selected_player.teamID:
                            success = building_clicked.add_to_training_queue(selected_player)
                            game_state['player_info_updated'] = True
                            if not success:
                                if 'insufficient_resources_feedback' not in game_state:
                                    game_state['insufficient_resources_feedback'] = {}
                                game_state['insufficient_resources_feedback'][building_clicked.entity_id] = time.time()
                else:
                    entity = closest_entity(game_state, mouse_x, mouse_y)
                    if entity:
                        select_single_entity(entity, game_state, ctrl_pressed)
                        if hasattr(entity, 'notify_clicked'):
                            entity.notify_clicked()
                    else:
                        handle_left_click_on_panels_or_start_box_selection(
                            mouse_x, 
                            mouse_y, 
                            game_state, 
                            ctrl_pressed
                        )

        elif event.button == 3:
            if selected_player and 'selected_units' in game_state and len(game_state['selected_units']) > 0:
                entity_target = closest_entity(game_state, mouse_x, mouse_y)
                for unit_selected in game_state['selected_units']:
                    unit_selected.set_target(entity_target)
                    unit_selected.path = None
                mouse_x, mouse_y = screen_to_2_5d(
                    mouse_x, mouse_y, screen_width, screen_height,
                    camera, HALF_TILE_SIZE , HALF_TILE_SIZE / 2
                )
                for unit_selected in game_state['selected_units']:
                    unit_selected.set_destination((mouse_x, mouse_y), game_state['game_map'])

        elif event.button == 4:
            camera.set_zoom(camera.zoom * 1.1)
        elif event.button == 5:
            camera.set_zoom(camera.zoom / 1.1)

    elif event.type == pygame.MOUSEMOTION:
        if game_state['minimap_dragging']:
            current_x, current_y = event.pos
            mini_rect = game_state['minimap_background_rect']
            local_x = current_x - mini_rect.x
            local_y = current_y - mini_rect.y

            scale = game_state['minimap_scale']
            offset_x = game_state['minimap_offset_x']
            offset_y = game_state['minimap_offset_y']
            map_min_iso_x = game_state['minimap_min_iso_x']
            map_min_iso_y = game_state['minimap_min_iso_y']

            iso_x = (local_x - offset_x) / scale + map_min_iso_x
            iso_y = (local_y - offset_y) / scale + map_min_iso_y

            camera.offset_x = -iso_x
            camera.offset_y = -iso_y
            camera.limit_camera()
        else:
            if game_state.get('selecting_entities', False):
                game_state['selection_end'] = event.pos

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            game_state['minimap_dragging'] = False
            if game_state.get('selecting_entities'):
                finalize_box_selection(game_state)

def select_single_entity(entity, game_state, ctrl_pressed):
    if 'selected_entities' not in game_state:
        game_state['selected_entities'] = []
    if 'selected_units' not in game_state:
        game_state['selected_units'] = []

    if not ctrl_pressed:
        game_state['selected_entities'].clear()
        game_state['selected_units'].clear()

    if entity not in game_state['selected_entities']:
        game_state['selected_entities'].append(entity)

    selected_player = game_state['selected_player']
    if selected_player and isinstance(entity, Unit):
        if entity.team == selected_player.teamID:
            if entity not in game_state['selected_units']:
                game_state['selected_units'].append(entity)

def handle_left_click_on_panels_or_start_box_selection(mouse_x, mouse_y, game_state, ctrl_pressed=False):
    players = game_state['players']
    screen_height = game_state['screen_height']
    minimap_rect = game_state['minimap_background_rect']
    button_height = 30
    padding = 5
    max_display_height = screen_height / 3

    columns = 1
    while columns <= 4:
        rows = (len(players) + columns - 1) // columns
        total_height = button_height * rows + padding * (rows - 1)
        if total_height <= max_display_height or columns == 4:
            break
        columns += 1

    button_width = (minimap_rect.width - padding * (columns - 1)) // columns
    rows = (len(players) + columns - 1) // columns
    total_height = button_height * rows + padding * (rows - 1)

    base_x = minimap_rect.x
    base_y = minimap_rect.y - total_height - padding

    camera = game_state['camera']
    clicked_player_panel = False

    from Controller.utils import to_isometric
    from Entity.Building import TownCentre

    for index, player_obj in enumerate(reversed(players)):
        col = index % columns
        row = index // columns
        rect_x = base_x + col * (button_width + padding)
        rect_y = base_y + row * (button_height + padding)
        panel_rect = pygame.Rect(rect_x, rect_y, button_width, button_height)

        if panel_rect.collidepoint(mouse_x, mouse_y):
            if game_state['selected_player'] != player_obj:
                game_state['selected_player'] = player_obj
                game_state['player_selection_updated'] = True
                game_state['player_info_updated'] = True
                for building_obj in player_obj.buildings:
                    if isinstance(building_obj, TownCentre):
                        iso_x, iso_y = to_isometric(
                            building_obj.x, 
                            building_obj.y, 
                            HALF_TILE_SIZE, 
                            HALF_TILE_SIZE / 2
                        )
                        camera.offset_x = -iso_x
                        camera.offset_y = -iso_y
                        camera.limit_camera()
                        break
            clicked_player_panel = True
            break

    if not clicked_player_panel:
        game_state['selecting_entities'] = True
        game_state['selection_start'] = (mouse_x, mouse_y)
        game_state['selection_end'] = (mouse_x, mouse_y)
        game_state['box_additive'] = ctrl_pressed

def finalize_box_selection(game_state):
    import pygame
    from Controller.utils import tile_to_screen

    x1, y1 = game_state['selection_start']
    x2, y2 = game_state['selection_end']
    select_rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
    select_rect.normalize()

    game_state['selecting_entities'] = False
    game_state['selection_start'] = None
    game_state['selection_end'] = None

    if 'selected_entities' not in game_state:
        game_state['selected_entities'] = []
    if 'selected_units' not in game_state:
        game_state['selected_units'] = []

    if not game_state.get('box_additive', False):
        game_state['selected_entities'].clear()
        game_state['selected_units'].clear()

    selected_player = game_state['selected_player']
    if not selected_player:
        return

    screen_width = game_state['screen_width']
    screen_height = game_state['screen_height']
    camera = game_state['camera']
    game_map = game_state['game_map']

    all_entities = set()
    for entities_set in game_map.grid.values():
        for entity_obj in entities_set:
            all_entities.add(entity_obj)

    for entity_obj in all_entities:
        screen_x, screen_y = tile_to_screen(
            entity_obj.x, 
            entity_obj.y,
            HALF_TILE_SIZE, 
            HALF_TILE_SIZE / 2,
            camera, 
            screen_width, 
            screen_height
        )
        if select_rect.collidepoint(screen_x, screen_y):
            if entity_obj not in game_state['selected_entities']:
                game_state['selected_entities'].append(entity_obj)

            if isinstance(entity_obj, Unit) and entity_obj.team == selected_player.teamID:
                if entity_obj not in game_state['selected_units']:
                    game_state['selected_units'].append(entity_obj)

def closest_entity(game_state, mouse_x, mouse_y, search_radius=2):
    game_map = game_state['game_map']
    camera = game_state['camera']
    screen_width = game_state['screen_width']
    screen_height = game_state['screen_height']
    mouse_2_5d = screen_to_2_5d(mouse_x, mouse_y, screen_width, screen_height, camera, HALF_TILE_SIZE, HALF_TILE_SIZE/2)

    tile_x, tile_y = screen_to_tile(
        mouse_x, mouse_y, 
        screen_width, screen_height, 
        camera, 
        HALF_TILE_SIZE / 2, 
        HALF_TILE_SIZE / 4
    )
    entity_set = game_map.grid.get((tile_x, tile_y), [])
    shortest_distance = 0
    closest_entity = None
    for entity in entity_set:
        distance = math.dist(mouse_2_5d,(entity.x, entity.y)) - entity.hitbox
        if distance < shortest_distance:
            shortest_distance = distance
            closest_entity = entity
    return closest_entity

def find_entity_by_id(game_state, entity_id):
    game_map = game_state['game_map']
    for position, entity_set in game_map.grid.items():
        for entity_obj in entity_set:
            if entity_obj.entity_id == entity_id:
                return entity_obj

    for position, entity_set in game_map.inactive_matrix.items():
        for entity_obj in entity_set:
            if entity_obj.entity_id == entity_id:
                return entity_obj
    return None
