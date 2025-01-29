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
    VALID_LEVELS
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
    current_input = ""  # Accumulate input characters

    while True:
        # Si on a déjà validé (peut arriver si l'utilisateur a cliqué dans le menu GUI),
        # on sort immédiatement.
        if user_choices["validated"]:
            return

        if step == 0:
            print("\n--- Choisir le mode d'affichage ---")
            print("[1] GUI only / [2] Terminal only / [3] Both ? (défaut=3)")
            step = 1
            current_input = ""

        elif step == 1:  # Display mode input
            pass  # Wait for input in the main loop

        elif step == 2:
            print("\n--- Menu Terminal ---")
            print("[1] Nouvelle partie / [2] Charger une sauvegarde ?")
            step = 3
            current_input = ""

        elif step == 3:  # New/Load game input
            pass  # Wait for input in the main loop

        elif step == 4:
            print("\n--- Paramètres de la nouvelle partie : ---")
            print(f"Largeur (multiples de 10, défaut={user_choices['grid_width']}) : ")
            step = 5
            current_input = ""

        elif step == 5:  # Width input
            pass  # Wait for input in the main loop

        elif step == 6:
            print(f"Hauteur (multiples de 10, défaut={user_choices['grid_height']}) : ")
            step = 7
            current_input = ""

        elif step == 7:  # Height input
            pass  # Wait for input in the main loop

        elif step == 8:
            print(f"Nb bots possibles : 1..55 (défaut={user_choices['num_bots']})")
            print("Nb bots : ")
            step = 9
            current_input = ""

        elif step == 9:  # Bots input
            pass  # Wait for input in the main loop

        elif step == 10:
            print("Niveaux possibles :", VALID_LEVELS)
            print(f"Niveau bots (défaut={user_choices['bot_level']}) : ")
            step = 11
            current_input = ""

        elif step == 11:  # Bot level input
            pass  # Wait for input in the main loop

        elif step == 12:
            # Choix du mode IA pour chaque bot
            pass  # Handled below in the input logic

        elif step == 13:  # Gold at center input
            pass  # Wait for input in the main loop

        # Lecture non bloquante
        char_in = get_input_non_blocking()
        if char_in is not None:
            char = char_in

            if char == '\r':  # Enter key pressed
                line = current_input.strip()
                if step == 1:  # Display mode
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
                    step = 2

                elif step == 3:  # New game / Load game
                    if line == '2':
                        user_choices["load_game"] = True
                        if os.path.isdir(SAVE_DIRECTORY):
                            saves = [f for f in os.listdir(SAVE_DIRECTORY) if f.endswith('.pkl')]
                            if saves:
                                print("Saves disponibles :")
                                for idx, sf in enumerate(saves):
                                    print(f"{idx+1} - {sf}")
                                print("Sélection de la sauvegarde : ")
                                step = 14
                            else:
                                print("Aucune sauvegarde => nouvelle partie.")
                                user_choices["load_game"] = False
                                step = 4
                        else:
                            print("Pas de répertoire => nouvelle partie.")
                            user_choices["load_game"] = False
                            step = 4
                    else:
                        user_choices["load_game"] = False
                        step = 4

                elif step == 14:  # Save selection
                    if line == "":
                        print("Pas de saisie => nouvelle partie.")
                        user_choices["load_game"] = False
                        step = 4
                    else:
                        try:
                            sel_idx = int(line) - 1
                            if 0 <= sel_idx < len(saves):
                                user_choices["chosen_save"] = os.path.join(SAVE_DIRECTORY, saves[sel_idx])
                                user_choices["validated_by"] = "terminal"
                                user_choices["validated"] = True
                                return
                            else:
                                print("Index invalide => nouvelle partie.")
                                user_choices["load_game"] = False
                                step = 4
                        except:
                            print("Choix invalide => nouvelle partie.")
                            user_choices["load_game"] = False
                            step = 4

                elif step == 5:  # Width input
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

                elif step == 7:  # Height input
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

                elif step == 9:  # Number of bots
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
                    step = 10

                elif step == 11:  # Bot level
                    if line == "":
                        print(f"Pas de saisie => niveau bots par défaut {user_choices['bot_level']}")
                    else:
                        if line in VALID_LEVELS:
                            user_choices["bot_level"] = line
                            print(f"Niveau bots : {line}")
                        else:
                            print(f"Valeur invalide => niveau bots par défaut {user_choices['bot_level']}")
                    user_choices["bot_modes"] = []
                    user_choices["current_bot_mode_index"] = 0
                    # Affichage de la première question de mode IA
                    if user_choices["num_bots"] > 0:
                        print("\nMode IA possibles: economique, defensif, offensif")
                        print(f"Choisir pour le Bot #1 (défaut=economique): ")
                        step = 12
                    else:
                        # S'il n'y a pas de bot, on saute directement
                        print("\nOr au centre ? (oui/non, défaut=non) : ")
                        step = 13

                elif step == 12:
                    # Choix individuel du mode IA pour chaque bot
                    idx = user_choices["current_bot_mode_index"]
                    nb_bots = user_choices["num_bots"]

                    if idx < nb_bots:
                        # Lecture du mode pour ce bot
                        if line == "":
                            chosen_mode = "economique"
                            print(f"Pas de saisie => Mode IA pour le Bot #{idx+1} = economique (défaut)")
                        else:
                            if line in ["economique", "defensif", "offensif"]:
                                chosen_mode = line
                                print(f"Mode IA pour le Bot #{idx+1} = {chosen_mode}")
                            else:
                                chosen_mode = "economique"
                                print(f"Choix invalide => Mode IA pour le Bot #{idx+1} = economique (défaut)")

                        user_choices["bot_modes"].append(chosen_mode)
                        user_choices["current_bot_mode_index"] += 1

                        # Y a-t-il encore un bot à paramétrer ?
                        if user_choices["current_bot_mode_index"] < nb_bots:
                            print("\nMode IA possibles: economique, defensif, offensif")
                            print(f"Choisir pour le Bot #{user_choices['current_bot_mode_index']+1} (défaut=economique): ")
                            step = 12
                        else:
                            print("\nOr au centre ? (oui/non, défaut=non) : ")
                            step = 13
                    else:
                        # On a déjà défini le mode de tous les bots
                        print("\nOr au centre ? (oui/non, défaut=non) : ")
                        step = 13

                elif step == 13:  # Gold at center
                    if line == "":
                        user_choices["gold_at_center"] = False
                        print("Pas de saisie => Or au centre = non (défaut)")
                    elif line.lower() in ["oui", "o"]:
                        user_choices["gold_at_center"] = True
                        print("Or au centre = oui")
                    elif line.lower() in ["non", "n"]:
                        user_choices["gold_at_center"] = False
                        print("Or au centre = non")
                    else:
                        print("Choix invalide => Or au centre = non (défaut)")
                        user_choices["gold_at_center"] = False
                    step = 15
                    user_choices["validated_by"] = "terminal"
                    user_choices["validated"] = True
                    return

                current_input = ""  # Reset input after processing

            elif char:
                # Accumulate character input
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
    Boucle principale avec un flag user_choices["validated"] :
    - Tant que validated n'est pas True, on lance le(s) menu(s) (GUI + Terminal).
    - Une fois la config validée, on instancie la partie (map, players).
    - On lance curses si nécessaire, on lance la game_loop (Pygame) si nécessaire.
    - Sur switch_display (F9), on arrête curses + pygame display, on bascule l'index,
      et on 'continue' la boucle, SANS relancer les menus (puisque validated = True).
    - Sur return_to_menu, on efface user_choices et on 'continue' pour relancer le menu.
    - Sur quit, on sort du while True.
    """
    game_map = None
    screen = None

    while True:
        if not user_choices["validated"]:
            if user_choices["index_terminal_display"] in [0, 2]:
                screen, sw, sh = init_pygame()
                print("DEBUG: Initialized Pygame for GUI or Both mode")

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
                print("DEBUG: Running Terminal menu only")
                ask_terminal_inputs_non_blocking()

        mode_index = user_choices["index_terminal_display"]
        if mode_index == 0:
            screen, sw, sh = init_pygame()
            print("DEBUG: GUI only mode: Initializing Pygame")
        elif mode_index == 1:
            sw, sh = (800, 600)
            screen = None
            print("DEBUG: Terminal only mode: No Pygame initialization, screen=None")
        elif mode_index == 2:
            screen, sw, sh = init_pygame()
            print("DEBUG: Both mode: Initializing Pygame")
        else:
            screen = None
            sw, sh = (800, 600)

        load_game   = user_choices["load_game"]
        chosen_save = user_choices["chosen_save"]
        grid_w      = user_choices["grid_width"]
        grid_h      = user_choices["grid_height"]
        nb_bots     = user_choices["num_bots"]
        bot_level   = user_choices["bot_level"]
        gold_c      = user_choices["gold_at_center"]
        validated_by = user_choices.get("validated_by")

        if load_game and chosen_save:
            if game_map is None:
                game_map = GameMap(0, False, [], generate=False)
            game_map.load_map(chosen_save)
            players = game_map.players
        else:
            players = init_players(nb_bots, bot_level)
            game_map = GameMap(grid_w, grid_h, gold_c, players)

        t_curses_started = False
        if mode_index in [1, 2]:
            t_curses_started = True
            t_curses = threading.Thread(
                target=start_terminal_interface,
                args=(game_map,),
                daemon=True
            )
            t_curses.start()
            print("DEBUG: Curses thread started for Terminal or Both mode")
        else:
            t_curses = None
            print("DEBUG: Curses not started for GUI only mode")

        if mode_index == 0:
            if screen is None:
                screen, sw, sh = init_pygame()
            if validated_by == "terminal":
                print("Loading des assets...")
                if not is_assets_loaded():
                    show_loading_screen_until_done(screen, sw, sh)
            elif validated_by != "terminal" and not is_assets_loaded():
                show_loading_screen_until_done(screen, sw, sh)
            print("DEBUG: GUI only mode, Pygame rendering will be used in game_loop")

        elif mode_index == 2:
            if screen is None:
                screen, sw, sh = init_pygame()
            if validated_by == "terminal":
                print("Loading des assets...")
                if not is_assets_loaded():
                    show_loading_screen_until_done(screen, sw, sh)
            elif validated_by != "terminal" and not is_assets_loaded():
                show_loading_screen_until_done(screen, sw, sh)
            print("DEBUG: Both mode, Pygame rendering AND Curses will be used")

        else:
            screen = None
            sw, sh = (800, 600)
            print("DEBUG: Terminal only mode, Pygame rendering will be skipped")

        print("DEBUG: Calling game_loop now...")

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
                "grid_width": 120,
                "grid_height": 120,
                "num_bots": 2,
                "bot_level": "lean",
                "gold_at_center": False,
                "validated": False,
                "validated_by": None,
                "menu_result": None,
                "bot_mode": "economique"
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
            print("[MAIN] Starting display switch process...")

            if not os.path.exists(TEMP_SAVE_PATH):
                game_map.save_map(TEMP_SAVE_PATH)
                print(f"[MAIN] Game state saved to {TEMP_SAVE_PATH}")

            if t_curses_started:
                stop_curses()
                if t_curses.is_alive():
                    t_curses.join()
                os.system('cls' if os.name == 'nt' else 'clear')
                t_curses_started = False
                print("[MAIN] Curses interface cleaned up")

            if pygame.display.get_init():
                pygame.display.quit()
            pygame.quit()
            print("[MAIN] Pygame display cleaned up")

            old_mode = user_choices["index_terminal_display"]
            if old_mode == 0:  # GUI->Terminal
                user_choices["index_terminal_display"] = 1
                screen = None
            elif old_mode == 1:  # Terminal->GUI
                user_choices["index_terminal_display"] = 0
            else:
                user_choices["index_terminal_display"] = 1
                screen = None

            user_choices["menu_result"] = None
            user_choices["validated"] = True

            time.sleep(0.2)
            print("[MAIN] Display switch preparation complete")
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
                "load_game": False,
                "chosen_save": "",
                "grid_width": 120,
                "grid_height": 120,
                "num_bots": 2,
                "bot_level": "lean",
                "gold_at_center": False,
                "validated": False,
                "validated_by": None,
                "menu_result": None
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
