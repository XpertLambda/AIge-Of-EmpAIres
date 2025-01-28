# Chemin: main.py
# Path: main.py
# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\main.py
import pygame
import os
import sys
import threading
import time
import platform
try:
    import msvcrt
except ImportError:
    msvcrt = None

from select import select

from Controller.init_map import init_pygame, game_loop
from Models.Map import GameMap
from Controller.init_player import init_players
from Controller.init_assets import load_sprites, ASSETS_LOADED, get_assets_progress, is_assets_loaded
from Settings.setup import SAVE_DIRECTORY
from Controller.gui import (
    run_gui_menu,
    user_choices,
    VALID_GRID_SIZES,
    VALID_BOTS_COUNT,
    VALID_LEVELS,
    VALID_BOT_MODES # Import VALID_BOT_MODES
)
from Controller.Bot import *

# Import du curses terminal display
from Controller.terminal_display import start_terminal_interface, stop_curses

from Settings.sync import TEMP_SAVE_PATH, TEMP_SAVE_FILENAME # Import TEMP_SAVE_PATH


def get_input_non_blocking():
    """Lecture non bloquante depuis stdin, compatible Windows/unix."""
    if platform.system() == "Windows" and msvcrt:
        if msvcrt.kbhit():
            return msvcrt.getwche()
        return None
    else:
        rlist, _, _ = select([sys.stdin], [], [], 0)
        if rlist:
            return sys.stdin.readline()
        return None


def ask_terminal_inputs_non_blocking():
    """
    Menu Terminal non-bloquant.
    [1] GUI only / [2] Terminal only / [3] Both ? (défaut=3)
    puis [1] nouvelle partie / [2] charger une sauvegarde, etc.
    On stocke le résultat dans user_choices et on met user_choices["validated"] = True à la fin.
    """
    step = 0
    saves = []
    current_input = "" # Accumulate input characters

    while True:
        # Si on a déjà validé (peut arriver si l'utilisateur a cliqué dans le menu GUI),
        # on sort immédiatement.
        if user_choices["validated"]:
            return

        if step == 0:
            print("\n--- Choisir le mode d'affichage ---")
            print("[1] GUI only / [2] Terminal only / [3] Both ? (défaut=3)")
            step = 1
            current_input = "" # Reset input for new step

        elif step == 1: # Display mode input
            pass # Wait for input in the main loop

        elif step == 2:
            print("\n--- Menu Terminal ---")
            print("[1] Nouvelle partie / [2] Charger une sauvegarde ?")
            step = 3
            current_input = ""

        elif step == 3: # New/Load game input
            pass # Wait for input in the main loop

        elif step == 4:
            print("\n--- Paramètres de la nouvelle partie : ---")
            print(f"Largeur (multiples de 10, défaut={user_choices['grid_width']}) : ")
            step = 5
            current_input = ""

        elif step == 5: # Width input
            pass # Wait for input in the main loop

        elif step == 6:
            print(f"Hauteur (multiples de 10, défaut={user_choices['grid_height']}) : ")
            step = 7
            current_input = ""

        elif step == 7: # Height input
            pass # Wait for input in the main loop

        elif step == 8:
            print(f"Nb bots possibles : 1..55 (défaut={user_choices['num_bots']})")
            print("Nb bots : ")
            step = 9
            current_input = ""

        elif step == 9: # Bots input
            pass # Wait for input in the main loop

        elif step == 10:
            print("Niveaux possibles :", VALID_LEVELS)
            print(f"Niveau bots (défaut={user_choices['bot_level']}) : ")
            step = 11
            current_input = ""

        elif step == 11: # Bot level input
            pass # Wait for input in the main loop

        elif step == 12:
            print("Or au centre ? (oui/non, défaut=non) : ")
            step = 13
            current_input = ""

        elif step == 13: # Gold at center input
            pass # Wait for input in the main loop

        elif step == 15:
            print("Modes IA disponibles :", VALID_BOT_MODES) # Afficher les modes disponibles
            print(f"Mode IA (défaut=economique) : ") # Demander le mode IA
            step = 16
            current_input = ""

        elif step == 16: # Bot mode input
            pass # Wait for input in the main loop


        # Lecture non bloquante
        char_in = get_input_non_blocking()
        if char_in is not None:
            char = char_in

            if char == '\r': # Enter key pressed (or equivalent for different OS)
                line = current_input.strip()
                print(f"DEBUG Terminal Input: Line='{line}', Step={step}") # DEBUG PRINT - Input received
                if step == 1: # Display mode
                    # Par défaut => both
                    if line == "":
                        user_choices["index_terminal_display"] = 2
                        print("Aucun choix => Both.")
                    elif line in ['1', '2', '3']:
                        val = int(line)
                        if val == 1:
                            user_choices["index_terminal_display"] = 0
                            print("Mode choisi : GUI only.")
                        elif val == 2:
                            user_choices["index_terminal_display"] = 1
                            print("Mode choisi : Terminal only.")
                        else:
                            user_choices["index_terminal_display"] = 2
                            print("Mode choisi : Both.")
                    else:
                        user_choices["index_terminal_display"] = 2
                        print("Choix invalide => Both.")
                    step = 2 # Move to Menu terminal choix

                elif step == 3: # New game / Load game
                    if line == '2':
                        user_choices["load_game"] = True
                        if os.path.isdir(SAVE_DIRECTORY):
                            saves = [f for f in os.listdir(SAVE_DIRECTORY) if f.endswith('.pkl')]
                            if saves:
                                print("Saves disponibles :")
                                for idx, sf in enumerate(saves):
                                    print(f"{idx+1} - {sf}")
                                print("Sélection de la sauvegarde : ")
                                step = 14 # Go to save selection step (was 12, corrected to 14 to avoid confusion with gold_at_center step numbering)
                            else:
                                print("Aucune sauvegarde => nouvelle partie.")
                                user_choices["load_game"] = False
                                step = 4  # Go to new game parameters
                        else:
                            print("Pas de répertoire => nouvelle partie.")
                            user_choices["load_game"] = False
                            step = 4 # Go to new game parameters
                    else:
                        user_choices["load_game"] = False
                        step = 4 # Go to new game parameters

                elif step == 14: # Save selection (was 12, corrected to 14)
                    if line == "":
                        print("Pas de saisie => nouvelle partie.")
                        user_choices["load_game"] = False
                        step = 4
                    else:
                        try:
                            sel_idx = int(line) - 1
                            if 0 <= sel_idx < len(saves):
                                user_choices["chosen_save"] = os.path.join(SAVE_DIRECTORY, saves[sel_idx])
                                user_choices["validated_by"] = "terminal" # Indicate terminal validation
                                user_choices["validated"] = True
                                return  # On sort, menu validé
                            else:
                                print("Index invalide => nouvelle partie.")
                                user_choices["load_game"] = False
                                step = 4
                        except:
                            print("Choix invalide => nouvelle partie.")
                            user_choices["load_game"] = False
                            step = 4

                elif step == 5: # Width input
                    if line == "":
                        print(f"Pas de saisie => largeur par défaut {user_choices['grid_width']}")
                    else:
                        if line.isdigit():
                            val = int(line)
                            if val in VALID_GRID_SIZES:
                                user_choices["grid_width"] = val
                                print(f"Largeur : {val}")
                            else:
                                print(f"Valeur invalide => largeur par défaut {user_choices['grid_width']}")
                    step = 6

                elif step == 7: # height input
                    if line == "":
                        print(f"Pas de saisie => hauteur par défaut {user_choices['grid_height']}")
                    else:
                        if line.isdigit():
                            val = int(line)
                            if val in VALID_GRID_SIZES:
                                user_choices["grid_height"] = val
                                print(f"hauteur : {val}")
                            else:
                                print(f"Valeur invalide => hauteur par défaut {user_choices['grid_height']}")
                    step = 8

                elif step == 9: # Number of bots
                    if line == "":
                        print(f"Pas de saisie => nb bots par défaut {user_choices['num_bots']}")
                    else:
                        if line.isdigit():
                            val = int(line)
                            if val in VALID_BOTS_COUNT:
                                user_choices["num_bots"] = val
                                print(f"Nb bots : {val}")
                            else:
                                print(f"Valeur invalide => nb bots par défaut {user_choices['num_bots']}")
                    step = 10 # Always move to step 10 after bot count

                elif step == 11: # Bot level
                    if line == "":
                        print(f"Pas de saisie => niveau bots par défaut {user_choices['bot_level']}")
                    else:
                        if line in VALID_LEVELS:
                            user_choices["bot_level"] = line
                            print(f"Niveau bots : {line}")
                        else:
                            print(f"Valeur invalide => niveau bots par défaut {user_choices['bot_level']}")
                    step = 12 # Always move to step 12 after bot level

                elif step == 13: # Gold at center (was 11, corrected to 13)
                    if line == "":
                        user_choices["gold_at_center"] = False
                        print("Pas de saisie => Or au centre = non (défaut)")
                    elif line.lower() == "oui" or line.lower() == "o":
                        user_choices["gold_at_center"] = True
                        print("Or au centre = oui")
                    elif line.lower() == "non" or line.lower() == "n":
                        user_choices["gold_at_center"] = False
                        print("Or au centre = non")
                    else:
                        print("Choix invalide => Or au centre = non (défaut)")
                        user_choices["gold_at_center"] = False
                    step = 15 # Move to bot mode selection

                elif step == 16: # Bot Mode selection (new step)
                    if line == "":
                        user_choices["bot_mode"] = "economique" # Default mode
                        print(f"Pas de saisie => Mode IA par défaut {user_choices['bot_mode']}")
                    elif line.lower() in VALID_BOT_MODES:
                        user_choices["bot_mode"] = line.lower()
                        print(f"Mode IA choisi : {line.lower()}")
                    else:
                        user_choices["bot_mode"] = "economique" # Default if invalid
                        print(f"Choix invalide => Mode IA par défaut {user_choices['bot_mode']}")
                    step = 17 # Move to final validation

                elif step == 17: # Final validation step (was 14, corrected to 17)
                    user_choices["validated_by"] = "terminal"
                    user_choices["validated"] = True
                    return # Validate and exit

                current_input = "" # Reset input after processing line

            elif char: # Accumulate character input
                current_input += char
                if platform.system() != "Windows":
                    sys.stdout.write(char)
                    sys.stdout.flush()

        time.sleep(0.005)


def background_load_assets(screen, sw, sh):
    """
    Cette fonction sera appelée en thread pour charger
    tous les assets sans bloquer la boucle principale.
    """
    load_sprites(screen, sw, sh, show_progress=False)


def show_loading_screen_until_done(screen, sw, sh):
    """
     Tant que tous les assets ne sont pas chargés,
     on affiche la barre de progression.
    """
    from Controller.init_assets import draw_progress_bar
    clock = pygame.time.Clock()

    running = True
    while running:
        # Autoriser la fermeture fenêtre via la croix
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        progress = get_assets_progress()

        # Exemple d'image de fond
        from Controller.init_assets import get_scaled_gui
        loading_screen = get_scaled_gui('loading_screen', variant=0, target_height=sh)

        draw_progress_bar(screen, progress, sw, sh, "Chargement en cours", loading_screen)

        if is_assets_loaded():
            running = False

        clock.tick(60)


def main():
    """
    Boucle principale avec gestion des menus et de la boucle de jeu.
    """
    game_map = None
    screen = None

    while True:
        if not user_choices["validated"]:
            if user_choices["index_terminal_display"] in [0, 2]:
                screen, sw, sh = init_pygame()

                t_assets = threading.Thread(
                    target=background_load_assets,
                    args=(screen, sw, sh)
                )
                t_assets.start()

                t_menu = threading.Thread(target=ask_terminal_inputs_non_blocking)
                t_menu.start()

                run_gui_menu(screen, sw, sh)

                if t_menu.is_alive():
                    t_menu.join()

                if not is_assets_loaded():
                    show_loading_screen_until_done(screen, sw, sh)
                if t_assets.is_alive():
                    t_assets.join()

            elif user_choices["index_terminal_display"] == 1:
                ask_terminal_inputs_non_blocking()


        mode_index  = user_choices["index_terminal_display"]
        load_game   = user_choices["load_game"]
        chosen_save = user_choices["chosen_save"]
        grid_w      = user_choices["grid_width"] # Use grid_width
        grid_h      = user_choices["grid_height"] # Use grid_height
        nb_bots     = user_choices["num_bots"]
        bot_level   = user_choices["bot_level"]
        gold_c      = user_choices["gold_at_center"]
        bot_mode    = user_choices.get("bot_mode", "economique") # Get bot_mode from user_choices, default to "economique"

        validated_by = user_choices.get("validated_by")
        game_state = {}

        if load_game and chosen_save:
            if game_map is None:
                game_map = GameMap(0, False, [], generate=False)
            game_map.load_map(chosen_save)
            if game_state:
               game_state['game_map'] = game_map
            players = game_map.players
        else:
            players = init_players(nb_bots, bot_level)
            game_map = GameMap(grid_w, grid_h, gold_c, players) # Use grid_w and grid_h

        t_curses_started = False
        if mode_index in [1, 2]:
            t_curses_started = True
            t_curses = threading.Thread(
                target=start_terminal_interface,
                args=(game_map,),
                daemon=True
            )
            t_curses.start()
        else:
            t_curses = None

        if mode_index == 0:
            if screen is None:
                screen, sw, sh = init_pygame()
            if validated_by == "terminal":
                if not is_assets_loaded():
                    show_loading_screen_until_done(screen, sw, sh)
            elif validated_by != "terminal" and not is_assets_loaded():
                show_loading_screen_until_done(screen, sw, sh)

        elif mode_index == 2:
            if screen is None:
                screen, sw, sh = init_pygame()
            if validated_by == "terminal":
                if not is_assets_loaded():
                    show_loading_screen_until_done(screen, sw, sh)
            elif validated_by != "terminal" and not is_assets_loaded():
                show_loading_screen_until_done(screen, sw, sh)

        else:
            screen = None
            sw, sh = (800, 600)

        clock = pygame.time.Clock()  # Create clock instance
        bots = [] # Initialize bots here, after players are created
        for player in players:
            bot = Bot(player, game_map, clock, difficulty=bot_level, mode=bot_mode) # Pass mode here
            bots.append(bot)


        from Controller.game_loop import game_loop
        game_loop_result = game_loop(screen, game_map, sw, sh, players)

        menu_result = user_choices.get("menu_result")

        if menu_result == "main_menu":
            if t_curses_started:
                stop_curses()
                if t_curses.is_alive():
                    t_curses.join()
            pygame.quit()
            game_map = None

            user_choices.clear()
            user_choices.update({
                "index_terminal_display": 2,
                "load_game": False,
                "chosen_save": "",
                "grid_width": 120, # Reset grid_width
                "grid_height": 120, # Reset grid_height
                "num_bots": 2,
                "bot_level": "lean",
                "gold_at_center": False,
                "validated": False,
                "validated_by": None,
                "menu_result": None,
                "bot_mode": "economique" # Reset bot_mode as well
            })
            continue

        elif menu_result == "quit":
            if t_curses_started:
                stop_curses()
                if t_curses.is_alive():
                    t_curses.join()
            pygame.quit()
            break

        elif menu_result == "switch_display":
            if t_curses_started:
                stop_curses()
                if t_curses.is_alive():
                    t_curses.join()
            pygame.quit()

            old_mode = user_choices["index_terminal_display"]
            if old_mode == 0:
                user_choices["index_terminal_display"] = 1
                screen = None
            elif old_mode == 1:
                user_choices["index_terminal_display"] = 0
            else:
                user_choices["index_terminal_display"] = 1

            user_choices["menu_result"] = None
            user_choices["validated"] = True
            continue

        if game_map.game_state.get('return_to_menu'):
            if t_curses_started:
                stop_curses()
                if t_curses.is_alive():
                    t_curses.join()
            pygame.quit()
            game_map = None

            user_choices.clear()
            user_choices.update({
                "index_terminal_display": 2,
                "load_game": False,
                "chosen_save": "",
                "grid_width": 120,
                "grid_height": 120,
                "num_bots": 2,
                "bot_level": "lean",
                "gold_at_center": False,
                "validated": False,
                "validated_by": None,
                "menu_result": None,
                "bot_mode": "economique" # Reset bot_mode
            })
            continue

        else:
            if t_curses_started:
                stop_curses()
                if t_curses.is_alive():
                    t_curses.join()
            pygame.quit()
            break


if __name__ == "__main__":
    main()