import pygame
import os
from Controller.init_map import init_pygame, game_loop
from Models.Map import GameMap
from Models.Team import Team
from Controller.init_player import init_players
from Controller.init_sprites import load_sprites
from Settings.setup import SAVE_DIRECTORY

def main():
    load_game = input("Voulez-vous charger une partie sauvegardée ? (oui/non) : ").lower() == 'oui'
    if load_game:
        # Liste les fichiers de sauvegarde disponibles
        save_files = [f for f in os.listdir(SAVE_DIRECTORY)
                      if f.endswith('.pkl') and os.path.isfile(os.path.join(SAVE_DIRECTORY, f))]
        if save_files:
            print("Saves disponibles :")
            for idx, filename in enumerate(save_files):
                print(f"{idx + 1}: {filename}")
            choice = int(input("Entrez le numéro de la sauvegarde à charger : ")) - 1
            if 0 <= choice < len(save_files):
                full_path = os.path.join(SAVE_DIRECTORY, save_files[choice])

                # Initialisation Pygame + écran
                screen, screen_width, screen_height = init_pygame()

                # Chargement de la map sans régénération
                game_map = GameMap(0, False, [], generate=False)
                game_map.load_map(full_path)

                # Récupère les joueurs de la sauvegarde
                players = game_map.players

                # Charge les sprites
                load_sprites(screen, screen_width, screen_height)

                # Lance la boucle de jeu avec les données chargées
                game_loop(screen, game_map, screen_width, screen_height, players)
            else:
                print("Choix invalide. Démarrage d'une nouvelle partie.")
                grid_size = int(input("Veuillez entrer la taille de la grille : "))
                number_of_players = int(input("Veuillez entrer le nombre de joueurs : "))
                gold_at_center_input = input("Voulez-vous de l'or au centre ? (oui/non) : ").lower()
                gold_at_center = gold_at_center_input == 'oui'

                screen, screen_width, screen_height = init_pygame()
                players = init_players(number_of_players)
                load_sprites(screen, screen_width, screen_height)
                game_map = GameMap(grid_size, gold_at_center, players)
                game_loop(screen, game_map, screen_width, screen_height, players)
        else:
            print("Aucune sauvegarde trouvée. Démarrage d'une nouvelle partie.")
            grid_size = int(input("Veuillez entrer la taille de la grille : "))
            number_of_players = int(input("Veuillez entrer le nombre de joueurs : "))
            gold_at_center_input = input("Voulez-vous de l'or au centre ? (oui/non) : ").lower()
            gold_at_center = gold_at_center_input == 'oui'

            screen, screen_width, screen_height = init_pygame()
            players = init_players(number_of_players)
            load_sprites(screen, screen_width, screen_height)
            game_map = GameMap(grid_size, gold_at_center, players)
            game_loop(screen, game_map, screen_width, screen_height, players)
    else:
        # Nouvelle partie
        grid_size = int(input("Veuillez entrer la taille de la grille : "))
        number_of_players = int(input("Veuillez entrer le nombre de joueurs : "))
        gold_at_center_input = input("Voulez-vous de l'or au centre ? (oui/non) : ").lower()
        gold_at_center = gold_at_center_input == 'oui'

        screen, screen_width, screen_height = init_pygame()
        players = init_players(number_of_players)
        load_sprites(screen, screen_width, screen_height)
        game_map = GameMap(grid_size, gold_at_center, players)
        game_loop(screen, game_map, screen_width, screen_height, players)

if __name__ == "__main__":
    main()
