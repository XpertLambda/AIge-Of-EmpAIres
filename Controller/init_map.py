import pygame
import sys
from Models.Map import GameMap
from Settings.setup import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT

# Initialisation de Pygame
def init_pygame():
    pygame.init()
    window_width = MAP_WIDTH
    window_height = MAP_HEIGHT
    screen = pygame.display.set_mode((window_width, window_height))
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
def draw_map(screen, game_map, textures):
    screen.fill((0, 0, 0))  # Effacer l'écran
    for y in range(game_map.height//TILE_SIZE):
        for x in range(game_map.width//TILE_SIZE):
            tile = game_map.grid[y][x]
            if tile.terrain_type == "grass":
                screen.blit(textures['grass'], (x * TILE_SIZE, y * TILE_SIZE))
            elif tile.terrain_type == "mountain":
                screen.blit(textures['mountain'], (x * TILE_SIZE, y * TILE_SIZE))  
            elif tile.terrain_type == "gold":
                screen.blit(textures['gold'], (x * TILE_SIZE, y * TILE_SIZE))
            elif tile.terrain_type == "wood":
                screen.blit(textures['wood'], (x * TILE_SIZE, y * TILE_SIZE))
            elif tile.terrain_type == "food":
                screen.blit(textures['food'], (x * TILE_SIZE, y * TILE_SIZE))
    pygame.display.flip()  # Mets à jour l'affichage

# Boucle principale du jeu
def game_loop(screen, game_map, textures):
    clock = pygame.time.Clock()
    FPS = 60
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Limiter la boucle à 60 images par seconde
        clock.tick(FPS)

    # Quitter le jeu proprement
    pygame.quit()
    sys.exit()


