# Chemin de /home/cyril/Documents/INSA/Projet_python/Controller/update.py
import pygame
from Models.html import write_full_html

def update_game_state(game_state, dt):
    """
    Each frame:
    1) camera movement
    2) if unit.target => unit.attack
    3) remove dead
    4) done
    """
    camera = game_state['camera']
    players= game_state['players']
    game_map= game_state['game_map']

    if not game_state.get('paused', False):
        handle_camera(camera, dt)

        # Attack logic
        for p in players:
            for u in p.units:
                if u.target:
                    u.attack(p, game_map, dt)

        # Remove dead
        for p in players:
            p.manage_life(game_map)

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
