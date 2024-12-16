import sys
# Chemin de Controller/init_map.py

import pygame
from Models.Map import GameMap
from Models.Team import Team
from Settings.setup import WINDOW_WIDTH, WINDOW_HEIGHT, DIFFICULTY
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
    # Demander les paramètres à l'utilisateur avant de lancer le jeu
    grid_size = int(input("Veuillez entrer la taille de la grille : "))
    number_of_players = int(input("Veuillez entrer le nombre de joueurs : "))
    gold_at_center_input = input("Voulez-vous de l'or au centre ? (oui/non) : ").lower()
    gold_at_center = gold_at_center_input == 'oui'

    screen, screen_width, screen_height = init_pygame()
    # Créer la game_map avec les paramètres donnés
    game_map = GameMap(grid_size, gold_at_center)
    # Initialiser les joueurs avec le nombre de joueurs spécifié
    players = init_players(number_of_players)

    # Démarrer la boucle de jeu
    game_loop(screen, game_map, screen_width, screen_height, players)
