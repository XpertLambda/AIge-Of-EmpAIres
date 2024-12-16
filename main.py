# main.py
import pygame  # Ensure pygame is imported here
from Controller.init_map import init_pygame, game_loop
from Models.Map import GameMap
from Models.Team import Team
from Controller.init_player import init_players
from Controller.init_sprites import load_sprites

def main():
    # Request game parameters from the user
    grid_size = int(input("Veuillez entrer la taille de la grille : "))
    number_of_players = int(input("Veuillez entrer le nombre de joueurs : "))
    gold_at_center_input = input("Voulez-vous de l'or au centre ? (oui/non) : ").lower()
    gold_at_center = gold_at_center_input == 'oui'

    # Déballer les retours de init_pygame
    screen, screen_width, screen_height = init_pygame()
    players = init_players(number_of_players)
    load_sprites(screen,screen_width,screen_height)
    # Initialiser la carte de jeu
    game_map = GameMap(grid_size, gold_at_center, players)
    game_map.print_map()
    # Lancer la boucle de jeu avec tous les arguments requis
    game_loop(screen, game_map, screen_width, screen_height, players)  

if __name__ == "__main__":
    main()