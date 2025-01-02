# Chemin de /home/cyril/Documents/INSA/Projet_python/Controller/event_handler.py
import pygame
import sys
import os
from tkinter import Tk, filedialog

from Entity.Building import Building, TownCentre
from Controller.isometric_utils import screen_to_tile, tile_to_screen
from Settings.setup import HALF_TILE_SIZE, SAVE_DIRECTORY
from Controller.drawing import compute_map_bounds, generate_team_colors
from Models.html import write_full_html
from AiUtils.aStar import a_star

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
        except:
            pass
        pygame.quit()
        sys.exit()

    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F2:
            game_state['show_all_health_bars'] = not game_state['show_all_health_bars']
        elif event.key == pygame.K_F11:
            game_state['game_map'].save_map()
            print("Game saved.")
        elif event.key == pygame.K_F12:
            # load logic
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
                    camera.offset_x=0
                    camera.offset_y=0
                    camera.zoom=1.0

                    min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_state['game_map'])
                    camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)
                    game_state['force_full_redraw'] = True
            except Exception as e:
                print(f"Error loading: {e}")
        # Zoom
        elif event.key == pygame.K_PLUS or event.key== pygame.K_KP_PLUS:
            camera.set_zoom(camera.zoom * 1.1)
        elif event.key == pygame.K_MINUS or event.key== pygame.K_KP_MINUS:
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
            game_state['paused'] = not game_state['paused']
            if game_state['paused']:
                write_full_html(game_state['players'], game_state['game_map'])

    elif event.type == pygame.MOUSEBUTTONDOWN:
        mx,my= event.pos
        if event.button== 1:
            # left => selection only
            if game_state['minimap_background_rect'].collidepoint(mx,my):
                game_state['minimap_dragging']=True
            else:
                clicked_entity = find_entity_for_building_or_unit(game_state, mx,my)
                if clicked_entity:
                    if hasattr(clicked_entity, "notify_clicked"):
                        clicked_entity.notify_clicked()
                else:
                    handle_left_click_panels_or_box(mx,my, game_state)
        elif event.button==3:
            # right => move or attack
            if selected_player and len(game_state['selected_units'])>0:
                # Clear old target
                for u in game_state['selected_units']:
                    u.target=None
                    u.path=None

                ent = find_entity_for_building_or_unit(game_state,mx,my)
                if ent:
                    # if enemy => attack
                    if ent.team!= selected_player.teamID:
                        for u in game_state['selected_units']:
                            u.target= ent
                    else:
                        # same team => move
                        tile_x, tile_y= screen_to_tile(mx,my, screen_width,screen_height,
                                                       camera, HALF_TILE_SIZE/2, HALF_TILE_SIZE/4)
                        for u in game_state['selected_units']:
                            a_star(u, (tile_x,tile_y), game_state['game_map'])
                else:
                    # empty => normal move
                    tile_x, tile_y= screen_to_tile(mx,my, screen_width, screen_height,
                                                   camera, HALF_TILE_SIZE/2, HALF_TILE_SIZE/4)
                    for u in game_state['selected_units']:
                        a_star(u, (tile_x,tile_y), game_state['game_map'])

        elif event.button==4:
            camera.set_zoom(camera.zoom * 1.1)
        elif event.button==5:
            camera.set_zoom(camera.zoom / 1.1)

    elif event.type == pygame.MOUSEMOTION:
        if game_state['minimap_dragging']:
            pass
        else:
            if game_state['selecting_units']:
                game_state['selection_end'] = event.pos

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button==1:
            game_state['minimap_dragging']=False
            if game_state['selecting_units']:
                finalize_box_selection(game_state)

def handle_left_click_panels_or_box(mx,my, game_state):
    # either user clicked player selection or do a box selection
    players= game_state['players']
    screen_h= game_state['screen_height']
    minimap_rect= game_state['minimap_background_rect']
    selection_height=30
    padding=5
    max_height= screen_h/3
    columns=1
    while columns<=4:
        rows=(len(players)+ columns-1)//columns
        total_h= selection_height*rows+ padding*(rows-1)
        if total_h<= max_height or columns==4:
            break
        columns+=1

    but_w= (minimap_rect.width- padding*(columns-1))//columns
    rows=(len(players)+ columns-1)//columns
    surface_h= selection_height* rows+ padding*(rows-1)
    but_x= minimap_rect.x
    but_y= minimap_rect.y- surface_h- padding

    clicked_player=False
    for index, p in enumerate(reversed(players)):
        col= index%columns
        row= index//columns
        rx= but_x+ col*(but_w+ padding)
        ry= but_y+ row*(selection_height+ padding)
        r= pygame.Rect(rx,ry, but_w, selection_height)
        if r.collidepoint(mx,my):
            if game_state['selected_player']!= p:
                game_state['selected_player']= p
                game_state['player_selection_updated']= True
                game_state['player_info_updated']=True
            clicked_player=True
            break

    if not clicked_player:
        game_state['selecting_units']= True
        game_state['selection_start']= (mx,my)
        game_state['selection_end']= (mx,my)

def finalize_box_selection(game_state):
    import pygame
    from Controller.isometric_utils import tile_to_screen
    x1,y1= game_state['selection_start']
    x2,y2= game_state['selection_end']
    rect= pygame.Rect(x1,y1, x2-x1, y2-y1)
    rect.normalize()

    game_state['selected_units'].clear()
    if game_state['selected_player']:
        all_u= game_state['selected_player'].units
        for u in all_u:
            sx,sy= tile_to_screen(u.x,u.y,
                                  HALF_TILE_SIZE, HALF_TILE_SIZE/2,
                                  game_state['camera'],
                                  game_state['screen_width'], game_state['screen_height'])
            if rect.collidepoint(sx,sy):
                game_state['selected_units'].append(u)

    game_state['selecting_units']=False
    game_state['selection_start']= None
    game_state['selection_end']= None

def find_entity_for_building_or_unit(game_state, mx,my, radius_tiles=0):
    from Controller.isometric_utils import screen_to_tile
    camera= game_state['camera']
    sw,sh= game_state['screen_width'], game_state['screen_height']
    tile_x, tile_y= screen_to_tile(mx,my, sw,sh, camera, HALF_TILE_SIZE/2, HALF_TILE_SIZE/4)
    gmap= game_state['game_map']

    candidates=[]
    for dx in range(-radius_tiles, radius_tiles+1):
        for dy in range(-radius_tiles, radius_tiles+1):
            nx, ny= tile_x+dx, tile_y+dy
            if 0<=nx< gmap.num_tiles_x and 0<=ny< gmap.num_tiles_y:
                candidates.append((nx,ny))

    for pos in candidates:
        es= gmap.grid.get(pos,None)
        if es:
            for e in es:
                return e
    return None
