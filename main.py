# main.py
import pygame  # Ensure pygame is imported here
from Controller.init_map import init_pygame, game_loop
from Models.Map import GameMap
from Models.Team import Team
from Controller.init_player import init_players
from Controller.init_sprites import load_sprites
from Settings.setup import NUMBER_OF_PLAYERS

def main():
    # Déballer les retours de init_pygame
    screen, screen_width, screen_height = init_pygame()
    players = init_players(NUMBER_OF_PLAYERS)
    load_sprites(screen,screen_width,screen_height)
    # Initialiser la carte de jeu
    game_map = GameMap(players)
    game_map.print_map()
    # Lancer la boucle de jeu avec tous les arguments requis
    game_loop(screen, game_map, screen_width, screen_height, players)  

if __name__ == "__main__":
    main()