import pygame
import sys
import os
from tkinter import Tk, filedialog

from Entity.Building import Building, TownCentre
from Controller.isometric_utils import screen_to_tile, tile_to_screen, to_isometric
from Settings.setup import HALF_TILE_SIZE, SAVE_DIRECTORY
from Controller.drawing import compute_map_bounds, generate_team_colors
from Models.html import write_full_html
from AiUtils.aStar import a_star
from Entity.Unit.Unit import Unit  

PANEL_RATIO = 0.25
BG_RATIO    = 0.20

def handle_events(event, game_state):
    camera = game_state['camera']
    players = game_state['players']
    selected_player = game_state['selected_player']
    screen_width = game_state['screen_width']
    screen_height = game_state['screen_height']

    if event.type == pygame.QUIT:
        try:
            os.remove('full_snapshot.html')
        except FileNotFoundError:
            pass
        pygame.quit()
        sys.exit()

    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F2:
            game_state['show_all_health_bars'] = not game_state['show_all_health_bars']
            print("show_all_health_bars =", game_state['show_all_health_bars'])

        elif event.key == pygame.K_F11:
            game_state['game_map'].save_map()
            print("Game saved.")

        elif event.key == pygame.K_F12:
            try:
                root = Tk()
                root.withdraw()
                chosen = filedialog.askopenfilename(initialdir=SAVE_DIRECTORY, filetypes=[("Pickle","*.pkl")])
                root.destroy()
                if chosen:
                    from Controller.drawing import create_minimap_background, compute_map_bounds, generate_team_colors
                    from Models.Map import GameMap
                    game_state['game_map'] = GameMap(0, False, [], generate=False)
                    game_state['game_map'].load_map(chosen)
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

                    min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_state['game_map'])
                    camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)
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
            except FileNotFoundError:
                pass
            pygame.quit()
            sys.exit()

    elif event.type == pygame.KEYUP:
        if event.key == pygame.K_TAB:
            game_state['paused'] = not game_state['paused']
            if game_state['paused']:
                write_full_html(game_state['players'], game_state['game_map'])

    elif event.type == pygame.MOUSEBUTTONDOWN:
        mx, my = event.pos
        mods = pygame.key.get_mods()
        ctrl_pressed = (mods & pygame.KMOD_CTRL)

        if event.button == 1:
            if game_state['minimap_background_rect'].collidepoint(mx, my):
                game_state['minimap_dragging'] = True
            else:
                clicked_entity = closest_entity(game_state, mx, my)
                if clicked_entity:
                    select_single_entity(clicked_entity, game_state, ctrl_pressed)
                    if hasattr(clicked_entity, "notify_clicked"):
                        clicked_entity.notify_clicked()
                else:
                    handle_left_click_panels_or_box(mx, my, game_state, ctrl_pressed)

        elif event.button == 3:
            # Clic droit => move ou attack
            if selected_player and len(game_state['selected_units']) > 0:
                # On vide l'ancien target/path
                for u in game_state['selected_units']:
                    u.set_target(None)
                    u.path = None

                ent = closest_entity(game_state, mx, my)
                for u in game_state['selected_units']:
                    u.set_target(ent)
                tile_x, tile_y = screen_to_tile(
                    mx, my, screen_width, screen_height,
                    camera, HALF_TILE_SIZE/2, HALF_TILE_SIZE/4
                )
                for u in game_state['selected_units']:
                   a_star(u, (tile_x, tile_y), game_state['game_map'])

        elif event.button == 4:
            camera.set_zoom(camera.zoom * 1.1)
        elif event.button == 5:
            camera.set_zoom(camera.zoom / 1.1)

    elif event.type == pygame.MOUSEMOTION:
        if game_state['minimap_dragging']:
            mouse_x, mouse_y = event.pos
            minimap_rect = game_state['minimap_background_rect']
            local_x = mouse_x - minimap_rect.x
            local_y = mouse_y - minimap_rect.y

            minimap_scale = game_state['minimap_scale']
            minimap_offset_x = game_state['minimap_offset_x']
            minimap_offset_y = game_state['minimap_offset_y']
            minimap_min_iso_x = game_state['minimap_min_iso_x']
            minimap_min_iso_y = game_state['minimap_min_iso_y']

            iso_x = (local_x - minimap_offset_x) / minimap_scale + minimap_min_iso_x
            iso_y = (local_y - minimap_offset_y) / minimap_scale + minimap_min_iso_y

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
    """
    Gère la sélection (ou multi-sélection si Ctrl)
    d'une entité via un *clic gauche unique*.
    """
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


def handle_left_click_panels_or_box(mx, my, game_state, ctrl_pressed=False):
    """
    Soit on clique sur un "bouton joueur", soit on démarre une box selection.
    """
    players = game_state['players']
    screen_h = game_state['screen_height']
    minimap_rect = game_state['minimap_background_rect']
    selection_height = 30
    padding = 5
    max_height = screen_h / 3

    columns = 1
    while columns <= 4:
        rows = (len(players) + columns - 1) // columns
        total_h = selection_height * rows + padding * (rows - 1)
        if total_h <= max_height or columns == 4:
            break
        columns += 1

    but_w = (minimap_rect.width - padding * (columns - 1)) // columns
    rows = (len(players) + columns - 1) // columns
    surface_h = selection_height * rows + padding * (rows - 1)
    but_x = minimap_rect.x
    but_y = minimap_rect.y - surface_h - padding

    camera = game_state['camera']
    clicked_player = False

    from Controller.isometric_utils import to_isometric
    from Entity.Building import TownCentre

    for index, p in enumerate(reversed(players)):
        col = index % columns
        row = index // columns
        rx = but_x + col*(but_w + padding)
        ry = but_y + row*(selection_height + padding)
        r = pygame.Rect(rx, ry, but_w, selection_height)
        if r.collidepoint(mx, my):
            if game_state['selected_player'] != p:
                game_state['selected_player'] = p
                game_state['player_selection_updated'] = True
                game_state['player_info_updated'] = True
                for bld in p.buildings:
                    if isinstance(bld, TownCentre):
                        iso_x, iso_y = to_isometric(
                            bld.x, bld.y,
                            HALF_TILE_SIZE, HALF_TILE_SIZE / 2
                        )
                        camera.offset_x = -iso_x
                        camera.offset_y = -iso_y
                        camera.limit_camera()
                        break
            clicked_player = True
            break

    if not clicked_player:
        game_state['selecting_entities'] = True
        game_state['selection_start'] = (mx, my)
        game_state['selection_end'] = (mx, my)
        game_state['box_additive'] = ctrl_pressed


def finalize_box_selection(game_state):
    """
    À la fin du clic-gauche maintenu, on détermine quelles entités 
    sont dans le rectangle de sélection. On stocke toutes ces entités dans
    `selected_entities`, et on stocke uniquement vos unités dans
    `selected_units`. Si Ctrl n'était pas appuyé, on écrase la sélection.
    """
    import pygame
    from Controller.isometric_utils import tile_to_screen

    x1, y1 = game_state['selection_start']
    x2, y2 = game_state['selection_end']
    rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
    rect.normalize()

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
    if selected_player is None:
        return

    sw = game_state['screen_width']
    sh = game_state['screen_height']
    camera = game_state['camera']
    gmap = game_state['game_map']

    all_ents = set()
    for ent_set in gmap.grid.values():
        for e in ent_set:
            all_ents.add(e)

    for e in all_ents:
        sx, sy = tile_to_screen(
            e.x, e.y,
            HALF_TILE_SIZE, HALF_TILE_SIZE / 2,
            camera, sw, sh
        )
        if rect.collidepoint(sx, sy):
            if e not in game_state['selected_entities']:
                game_state['selected_entities'].append(e)
            if isinstance(e, Unit) and e.team == selected_player.teamID:
                if e not in game_state['selected_units']:
                    game_state['selected_units'].append(e)

def closest_entity(game_state, mx, my, search_radius=2):
    gmap = game_state['game_map']
    camera = game_state['camera']
    sw = game_state['screen_width']
    sh = game_state['screen_height']
    entity = None
    tile_x, tile_y = screen_to_tile(mx, my, sw, sh, camera, HALF_TILE_SIZE/2, HALF_TILE_SIZE/4)
    entites = gmap.grid.get((tile_x, tile_y), [])
    if entites:
        entity = next(iter(entites))
    return entity
