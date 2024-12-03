# Chemin de Controller/init_map.py

import pygame
from Models.Map import GameMap
from Models.Team import Team
from Settings.setup import WINDOW_WIDTH, WINDOW_HEIGHT, DIFFICULTY, NUMBER_OF_PLAYERS
from Controller.game_loop import game_loop

def init_pygame():
    pygame.init()
    pygame.display.set_caption("Age of Empires - Version Python")
    
    # Obtenir la résolution actuelle de l'écran
    infoObject = pygame.display.Info()
    screen_width = infoObject.current_w
    screen_height = infoObject.current_h
    
    # Initialiser la fenêtre en mode plein écran
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    
    return screen, screen_width, screen_height

if __name__ == "__main__":
    screen, screen_width, screen_height = init_pygame()
    # Créer ou charger votre game_map et vos joueurs ici
    game_map = GameMap()
    # Initialisez vos joueurs
    players = []
    for i in range(1, NUMBER_OF_PLAYERS + 1):
        player = Team(DIFFICULTY, i)
        players.append(player)

    # Démarrer la boucle de jeu
    game_loop(screen, game_map, screen_width, screen_height, players)  # Paramètre modifié
