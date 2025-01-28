# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\main.py
# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\main.py
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

        elif step == 2:
            print("\n--- Menu Terminal ---")
            print("[1] Nouvelle partie / [2] Charger une sauvegarde ?")
            step = 3
            current_input = ""

        elif step == 4:
            print("\n--- Paramètres de la nouvelle partie : ---")
            print("Tailles possibles :", VALID_GRID_SIZES)
            print(f"Taille (défaut={user_choices['grid_size']}) : ")
            step = 5
            current_input = ""

        elif step == 6:
            print(f"Nb bots possibles : 1..55 (défaut={user_choices['num_bots']})")
            print("Nb bots : ")
            step = 7
            current_input = ""

        elif step == 8:
            print("Niveaux possibles :", VALID_LEVELS)
            print(f"Niveau bots (défaut={user_choices['bot_level']}) : ")
            step = 9
            current_input = ""

        elif step == 10:
            print("Or au centre ? (oui/non, défaut=non) : ")
            step = 11
            current_input = ""

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
                    step = 2 # Always move to step 2 after display mode

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
                                step = 12 # Go to save selection step
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

                elif step == 12: # Save selection
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

                elif step == 5: # Grid size
                    if line == "":
                        print(f"Pas de saisie => taille par défaut {user_choices['grid_size']}")
                    else:
                        if line.isdigit():
                            val = int(line)
                            if val in VALID_GRID_SIZES:
                                user_choices["grid_size"] = val
                                print(f"Taille : {val}")
                    step = 6 # Always move to step 6 after grid size

                elif step == 7: # Number of bots
                    if line == "":
                        print(f"Pas de saisie => nb bots par défaut {user_choices['num_bots']}")
                    else:
                        if line.isdigit():
                            val = int(line)
                            if val in VALID_BOTS_COUNT:
                                user_choices["num_bots"] = val
                                print(f"Nb bots : {val}")
                    step = 8 # Always move to step 8 after bot count

                elif step == 9: # Bot level
                    if line == "":
                        print(f"Pas de saisie => niveau bots par défaut {user_choices['bot_level']}")
                    else:
                        if line in VALID_LEVELS:
                            user_choices["bot_level"] = line
                            print(f"Niveau bots : {line}")
                    step = 10 # Always move to step 10 after bot level

                elif step == 11: # Corrected step number here
                    if line == "":
                        user_choices["gold_at_center"] = False
                        step = 13
                    elif line.lower() == "oui" or line.lower() == "o":
                        user_choices["gold_at_center"] = True
                        step = 13
                    elif line.lower() == "non" or line.lower() == "n":
                        user_choices["gold_at_center"] = False
                        step = 13
                    else:
                        print("Choix invalide, default = non")
                        user_choices["gold_at_center"] = False
                        step = 13

                if step == 13:
                    user_choices["validated_by"] = "terminal" # Indicate terminal validation
                    user_choices["validated"] = True
                    return
                current_input = "" # Reset input after processing line

            elif char: # Accumulate character input
                current_input += char
                if platform.system() != "Windows": # Conditionally echo for non-Windows
                    sys.stdout.write(char) # Echo character to terminal
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
    game_map = None  # Initialize game_map outside the loop

    # -- Boucle globale --
    while True:

        # 1) Si le menu n'est pas validé, on le lance (GUI ou Terminal, ou les 2).
        if not user_choices["validated"]:
            # Selon index_terminal_display, on peut initialiser Pygame ou non
            if user_choices["index_terminal_display"] in [0, 2]:
                # On initialise la fenêtre Pygame
                screen, sw, sh = init_pygame()
                print("DEBUG: Initialized Pygame for GUI or Both mode") # DEBUG

                # Lancement du chargement asynchrone des assets
                t_assets = threading.Thread(
                    target=background_load_assets,
                    args=(screen, sw, sh)
                )
                t_assets.start()

                # Lancement d'un thread pour lire les entrées Terminal en // (optionnel)
                t_menu = threading.Thread(target=ask_terminal_inputs_non_blocking)
                t_menu.start()

                # Lance le menu GUI
                run_gui_menu(screen, sw, sh)

                # Attendre la fin du thread menu
                if t_menu.is_alive():
                    t_menu.join()

                # Si assets pas chargés, afficher l'écran de chargement
                if not is_assets_loaded():
                    show_loading_screen_until_done(screen, sw, sh)
                if t_assets.is_alive():
                    t_assets.join()

            elif user_choices["index_terminal_display"] == 1: # Changed to elif for clarity
                # index_terminal_display == 1 => Terminal only
                print("DEBUG: Running Terminal menu only") # DEBUG
                # On peut directement lancer la lecture terminal
                # (Bloquante ou non-bloquante selon vos préférences)
                ask_terminal_inputs_non_blocking()

            # A ce stade, user_choices["validated"] = True => fin de la phase de menu
            # (soit dans le menu GUI, soit dans le menu Terminal).

        # 2) On a forcément sw, sh si on est passé par GUI, sinon on pose un fallback :
        mode_index = user_choices["index_terminal_display"] # Get mode_index here for clarity

        if mode_index == 0: # GUI only
            # GUI only => on initialise pygame
            screen, sw, sh = init_pygame()
            print("DEBUG: GUI only mode: Initializing Pygame") # DEBUG
        elif mode_index == 1: # Terminal only
            # Terminal only => no pygame initialization, fallback resolution
            sw, sh = (800, 600)  # Valeurs de secours
            screen = None # Ensure screen is None for terminal mode
            print("DEBUG: Terminal only mode: No Pygame initialization, screen=None") # DEBUG
        elif mode_index == 2: # Both
            # Both => initialise pygame
            screen, sw, sh = init_pygame()
            print("DEBUG: Both mode: Initializing Pygame") # DEBUG
        else: # Fallback/Error case
            screen = None
            sw, sh = (800, 600)



        mode_index  = user_choices["index_terminal_display"]
        load_game   = user_choices["load_game"]
        chosen_save = user_choices["chosen_save"]
        grid_size   = user_choices["grid_size"]
        nb_bots     = user_choices["num_bots"]
        bot_level   = user_choices["bot_level"]
        gold_c      = user_choices["gold_at_center"]
        validated_by = user_choices.get("validated_by")
        game_state = {} # create game_state here to pass it to load_map

        # 3) Création ou chargement de la map + players
        if load_game and chosen_save:
            if game_map is None: # Only create GameMap instance if it's None
                game_map = GameMap(0, False, [], generate=False)
            game_map.load_map(chosen_save) # Load into the existing game_map instance
            if game_state:
               game_state['game_map'] = game_map # update game_map in game_state as well

            players = game_map.players
        else:
            players = init_players(nb_bots, bot_level)
            game_map = GameMap(grid_size, gold_c, players) # Create a new GameMap instance if not loading

        # 4) Lancement *éventuel* de curses si mode_index in [1, 2]
        t_curses_started = False
        if mode_index in [1, 2]:
            t_curses_started = True
            t_curses = threading.Thread(
                target=start_terminal_interface,
                args=(game_map,),
                daemon=True
            )
            t_curses.start()
            print("DEBUG: Curses thread started for Terminal or Both mode") # DEBUG
        else:
            t_curses = None
            print("DEBUG: Curses not started for GUI only mode") # DEBUG

        # 5) Lancement éventuel du rendu Pygame si mode_index in [0, 2], sinon game_loop fait un "terminal" update
        if mode_index == 0: # Changed to elif and corrected condition
            if screen is None: # Check if screen is None (meaning not initialized yet)
                screen, sw, sh = init_pygame() # Initialize Pygame only if screen is None
            if validated_by == "terminal":
                print("Loading des assets...") # Simple print for terminal validation
            elif validated_by != "terminal" and not is_assets_loaded(): # Loading screen only if not terminal validated and assets not loaded
                show_loading_screen_until_done(screen, sw, sh)
            print("DEBUG: GUI only mode, Pygame rendering will be used in game_loop") # DEBUG
        elif mode_index == 2: # Explicitly handle 'Both' mode
            if screen is None: # Check if screen is None (meaning not initialized yet)
                screen, sw, sh = init_pygame() # Initialize Pygame only if screen is None
            if validated_by == "terminal":
                print("Loading des assets...") # Simple print for terminal validation
            elif validated_by != "terminal" and not is_assets_loaded(): # Loading screen only if not terminal validated and assets not loaded
                show_loading_screen_until_done(screen, sw, sh)
            print("DEBUG: Both mode, Pygame rendering AND Curses will be used") # DEBUG
        else: # mode_index == 1, Terminal only
            screen = None # Ensure screen is None for terminal only mode
            sw, sh = (800, 600) # Add fallback sw, sh for terminal mode
            print("DEBUG: Terminal only mode, Pygame rendering will be skipped") # DEBUG


        print("DEBUG: Calling game_loop now...") # DEBUG PRINT

        # 6) Boucle de jeu
        #    On utilise la fonction game_loop(...) qui peut (ou non) dessiner,
        #    en fonction de screen != None.  Elle écoute F9 => switch_display,
        #    ESC => quitte, etc.
        from Controller.game_loop import game_loop
        game_loop_result = game_loop(screen, game_map, sw, sh, players) # Pass the game_map object

        # 7) Regarder la sortie
        menu_result = user_choices.get("menu_result")

        # a) Menu principal => on y retourne
        if menu_result == "main_menu":
            # Fermer curses si lancé
            if t_curses_started:
                stop_curses()
                if t_curses.is_alive():
                    t_curses.join()
            # Fermer la fenêtre Pygame
            pygame.quit()
            game_map = None # Reset game_map when returning to main menu

            # On efface user_choices pour relancer la config complète
            user_choices.clear()
            user_choices.update({
                "index_terminal_display": 2,  # Par défaut on peut choisir "both"
                "load_game": False,
                "chosen_save": "",
                "grid_size": 120,
                "num_bots": 2,
                "bot_level": "lean",
                "gold_at_center": False,
                "validated": False,
                "validated_by": None, # Reset validation source
                "menu_result": None
            })
            # On relance la boucle => le menu sera rouvert
            continue

        # b) Quit => on sort du while True => fin du programme
        elif menu_result == "quit":
            if t_curses_started:
                stop_curses()
                if t_curses.is_alive():
                    t_curses.join()
            pygame.quit()
            break

        # c) Switch display => on bascule index 0 <-> 1, ou 2 -> 1, etc.
        elif menu_result == "switch_display":
            print("DEBUG: Switch display mode requested.") # DEBUG
            # 1. Save the game state
            game_map.save_map(TEMP_SAVE_PATH)
            print(f"DEBUG: Game saved to {TEMP_SAVE_PATH} before display switch.") # DEBUG

            # 2. Fermer curses si lancé
            if t_curses_started:
                stop_curses()
                if t_curses.is_alive():
                    t_curses.join()
                print("DEBUG: Curses stopped.") # DEBUG

            # 3. Fermer la fenêtre pygame
            pygame.display.quit()
            print("DEBUG: Pygame display quit.") # DEBUG

            # 4. Basculer l'index d'affichage
            if user_choices["index_terminal_display"] == 0:
                user_choices["index_terminal_display"] = 1  # passe GUI->Terminal
                print("DEBUG: Switched to Terminal only mode.") # DEBUG
            elif user_choices["index_terminal_display"] == 1:
                user_choices["index_terminal_display"] = 0  # Terminal->GUI
                print("DEBUG: Switched to GUI only mode.") # DEBUG
            else:
                # Si on était en both, on décide de passer en Terminal only (exemple)
                user_choices["index_terminal_display"] = 1
                print("DEBUG: Switched from Both to Terminal only mode.") # DEBUG

            # On retire "menu_result"
            user_choices["menu_result"] = None

            # 5. Delete the temporary save file
            try:
                os.remove(TEMP_SAVE_PATH)
                print(f"DEBUG: Temporary save file {TEMP_SAVE_PATH} deleted.") # DEBUG
            except FileNotFoundError:
                print(f"DEBUG: Temporary save file {TEMP_SAVE_PATH} not found, no deletion needed.") # DEBUG
            except Exception as e:
                print(f"DEBUG: Error deleting temporary save file: {e}") # DEBUG


            # ATTENTION : on ne remet pas validated = False => on ne relance PAS le menu
            # On se contente de redémarrer la partie avec la nouvelle config
            continue

        # d) Si le game_map signale un return_to_menu
        if game_map.game_state.get('return_to_menu'):
            if t_curses_started:
                stop_curses()
                if t_curses.is_alive():
                    t_curses.join()
            pygame.quit()
            game_map = None # Reset game_map when returning to menu

            # On ré-initialise user_choices => ce qui relancera le menu
            user_choices.clear()
            user_choices.update({
                #"index_terminal_display": 2,
                "load_game": False,
                "chosen_save": "",
                "grid_size": 120,
                "num_bots": 2,
                "bot_level": "lean",
                "gold_at_center": False,
                "validated": False,
                "validated_by": None, # Reset validation source
                "menu_result": None
            })
            continue

        # e) Sinon => fin
        else:
            # Ni switch_display, ni main_menu, ni quit => on sort
            if t_curses_started:
                stop_curses()
                if t_curses.is_alive():
                    t_curses.join()
            pygame.quit()
            break


if __name__ == "__main__":
    main()