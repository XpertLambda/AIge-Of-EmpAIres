import pygame
import os
import sys
import threading
from Controller.init_map import init_pygame, game_loop
from Models.Map import GameMap
from Controller.init_player import init_players
from Controller.init_assets import load_sprites
from Settings.setup import SAVE_DIRECTORY
from Controller.menu import run_gui_menu, ask_terminal_inputs, user_choices

def main():
    screen, screen_width, screen_height = init_pygame()
    load_sprites(screen, screen_width, screen_height)

    # Launch the terminal in a separate thread
    terminal_thread = threading.Thread(target=ask_terminal_inputs)
    terminal_thread.start()

    # Run GUI in the main thread
    run_gui_menu(screen, screen_width, screen_height)

    # If GUI just validated, kill the terminal thread
    if user_choices["validated"] and terminal_thread.is_alive():
        # This forcibly ends the thread so the game can proceed
        # (In Python, there's no safe direct thread kill, so we do an exit check in the thread.)
        pass
    elif not user_choices["validated"]:
        terminal_thread.join()

    # Récupération finale des paramètres
    grid_size     = user_choices["grid_size"]
    number_of_bots= user_choices["num_bots"]
    bot_level     = user_choices["bot_level"]  # si vous en avez besoin plus tard
    gold_at_center= user_choices["gold_at_center"]
    load_game     = user_choices["load_game"]
    chosen_save   = user_choices["chosen_save"]

    # Lance ensuite la partie
    if load_game and chosen_save:
        screen, screen_width, screen_height = init_pygame()
        game_map = GameMap(0, False, [], generate=False)
        game_map.load_map(chosen_save)
        print("Carte chargée :", chosen_save)
        game_map.display_map_in_terminal()
        players = game_map.players
        game_loop(screen, game_map, screen_width, screen_height, players)
    else:
        # Nouvelle partie
        players = init_players(number_of_bots)
        game_map = GameMap(grid_size, gold_at_center, players)
        game_loop(screen, game_map, screen_width, screen_height, players)

if __name__ == "__main__":
    main()
