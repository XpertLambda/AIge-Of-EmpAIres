# main.py

from Controller.init_map import init_pygame, game_loop
from Models.Map import GameMap

def main():
    # Déballer les retours de init_pygame
    screen, screen_width, screen_height = init_pygame()
    
    # Initialiser la carte de jeu
    game_map = GameMap()
    game_map.print_map()  # Affiche la carte dans la console pour le débogage
    
    # Lancer la boucle de jeu avec tous les arguments requis
    game_loop(screen, game_map, screen_width, screen_height)

if __name__ == "__main__":
    main()
