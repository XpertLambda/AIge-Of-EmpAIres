# Chemin de /home/cyril/Documents/INSA/Projet_python/Controller/update.py
import pygame
from Models.html import write_full_html

def update_game_state(game_state, dt):
    camera = game_state['camera']
    players= game_state['players']
    game_map= game_state['game_map']

    if not game_state.get('paused', False):
        handle_camera(camera, dt)

        for player in players:
            for unit in player.units:
                if unit.isAlive():
                    unit.setIdle()
                    if unit.path:
                        unit.move(game_map, dt)
                        unit.display_path(game_state['screen'], game_state['screen_width'], game_state['screen_height'], game_state['camera'])
                    if unit.target:
                            unit.attack(game_map, dt)
                else:
                    unit.kill(game_map)
        for inactive_entities in list(game_map.inactive_matrix.values()):
            if inactive_entities:
                for entity in list(inactive_entities):
                    entity.death(game_map)  

def handle_camera(camera, dt):
    import pygame
    keys= pygame.key.get_pressed()
    speed= 300* dt
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        speed*=2.5

    dx,dy=0,0
    if keys[pygame.K_q] or keys[pygame.K_LEFT]:
        dx+= speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx-= speed
    if keys[pygame.K_z] or keys[pygame.K_UP]:
        dy+= speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy-= speed

    if dx!=0 or dy!=0:
        camera.move(dx, dy)
