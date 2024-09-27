# Controller/init_map.py
import pygame
import sys
from Models.Map import GameMap
from Settings.setup import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, TILES_IN_VIEW, WINDOW_WIDTH, WINDOW_HEIGHT
from Controller.map_2_5d import draw_map

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width * TILE_SIZE, height * TILE_SIZE)

    def apply(self, entity):
        return entity.rect.move(-self.camera.topleft)

    def update(self, target):
        x = target.rect.centerx - self.camera.width // 2
        y = target.rect.centery - self.camera.height // 2
        self.camera = pygame.Rect(x, y, self.camera.width, self.camera.height)

def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Age of Empires - Python Version")
    return screen

def load_textures():
    return {}  # Retourne un dictionnaire vide car nous n'utilisons pas de textures

def game_loop(screen, game_map, textures):
    clock = pygame.time.Clock()
    camera = Camera(TILES_IN_VIEW, TILES_IN_VIEW)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:  # Z
            if camera.camera.top > 0:  # Vérifie si on peut déplacer vers le haut
                camera.camera.y -= 5
        if keys[pygame.K_s]:  # S
            if camera.camera.bottom < game_map.height:  # Vérifie si on peut déplacer vers le bas
                camera.camera.y += 5
        if keys[pygame.K_q]:  # Q
            if camera.camera.left > 0:  # Vérifie si on peut déplacer vers la gauche
                camera.camera.x -= 5
        if keys[pygame.K_d]:  # D
            if camera.camera.right < game_map.width:  # Vérifie si on peut déplacer vers la droite
                camera.camera.x += 5

        draw_map(screen, game_map, textures, camera)  # Dessiner la carte avec la caméra

        # Limiter la boucle à 120 images par seconde
        clock.tick(120)

    pygame.quit()
    sys.exit()