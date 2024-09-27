import pygame
import sys
from Models.Map import GameMap
from Settings.setup import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, TILES_IN_VIEW, WINDOW_WIDTH, WINDOW_HEIGHT

# Constantes pour la caméra


class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width * TILE_SIZE, height * TILE_SIZE)

    def apply(self, entity):
        return entity.rect.move(-self.camera.topleft)

    def update(self, target):
        x = target.rect.centerx - self.camera.width // 2
        y = target.rect.centery - self.camera.height // 2
        self.camera = pygame.Rect(x, y, self.camera.width, self.camera.height)

# Initialisation de Pygame
def init_pygame():
    pygame.init()
    window_width = MAP_WIDTH
    window_height = MAP_HEIGHT
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Age of Empires - Python Version")
    return screen

# Chargement des textures
def load_textures():
    grass_texture = pygame.image.load('assets/grass.png')
    grass_texture = pygame.transform.scale(grass_texture, (TILE_SIZE, TILE_SIZE))
    moutain_texture = pygame.image.load('assets/mountain.jpg')
    moutain_texture = pygame.transform.scale(moutain_texture, (TILE_SIZE, TILE_SIZE))
    food_texture = pygame.image.load('assets/food.png')
    food_texture = pygame.transform.scale(food_texture, (TILE_SIZE, TILE_SIZE))
    wood_texture = pygame.image.load('assets/wood.png')
    wood_texture = pygame.transform.scale(wood_texture, (TILE_SIZE, TILE_SIZE))
    gold_texture = pygame.image.load('assets/gold.png')
    gold_texture = pygame.transform.scale(gold_texture, (TILE_SIZE, TILE_SIZE))
    
    return {'grass': grass_texture, 
            'mountain': moutain_texture,
            'food': food_texture,
            'wood': wood_texture,
            'gold': gold_texture}

# Dessin de la carte
def draw_map(screen, game_map, textures, camera):
    screen.fill((0, 0, 0))  # Effacer l'écran
    for y in range(game_map.height//TILE_SIZE):
        for x in range(game_map.width//TILE_SIZE):
            tile = game_map.grid[y][x]
            if tile.terrain_type == "grass":
                screen.blit(textures['grass'], (x * TILE_SIZE - camera.camera.x, y * TILE_SIZE - camera.camera.y))
            elif tile.terrain_type == "mountain":
                screen.blit(textures['mountain'], (x * TILE_SIZE - camera.camera.x, y * TILE_SIZE - camera.camera.y))  
            elif tile.terrain_type == "gold":
                screen.blit(textures['gold'], (x * TILE_SIZE - camera.camera.x, y * TILE_SIZE - camera.camera.y))
            elif tile.terrain_type == "wood":
                screen.blit(textures['wood'], (x * TILE_SIZE - camera.camera.x, y * TILE_SIZE - camera.camera.y))
            elif tile.terrain_type == "food":
                screen.blit(textures['food'], (x * TILE_SIZE - camera.camera.x, y * TILE_SIZE - camera.camera.y))
    pygame.display.flip()  # Mets à jour l'affichage

# Boucle principale du jeu
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

