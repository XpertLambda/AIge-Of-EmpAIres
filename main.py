import pygame
import os
import sys
import threading
import time
from select import select

# -- Vos imports habituels --
from Controller.init_map import init_pygame, game_loop
from Models.Map import GameMap
from Controller.init_player import init_players
from Controller.init_assets import load_sprites
from Settings.setup import SAVE_DIRECTORY
from Controller.gui import run_gui_menu, user_choices, VALID_GRID_SIZES, VALID_BOTS_COUNT, VALID_LEVELS

def ask_terminal_inputs_non_blocking():
    """
    Menu Terminal en mode non-bloquant.
    On ajoute ici la possibilité de choisir :
       [1] GUI only
       [2] Terminal only
       [3] Both
    par défaut => "3" (Both).

    Ensuite, menu standard : [1] nouvelle partie / [2] load, etc.
    """

    step = 0  # État de progression dans les questions
    saves = []

    while True:
        # Si la GUI a validé, on arrête immédiatement
        if user_choices["validated"]:
            print("Choix fait sur la GUI => arrêt du menu terminal.")
            return

        if step == 0:
            print("\n--- Choisir le mode d'affichage ---")
            print("[1] GUI only / [2] Terminal only / [3] Both ? (défaut=3)")
            step = 1

        elif step == 2:
            print("\n--- Menu Terminal ---")
            print("[1] Nouvelle partie / [2] Charger une sauvegarde ?")
            step = 3

        elif step == 4:
            # On va afficher les paramètres pour la nouvelle partie
            print("\n--- Paramètres de la nouvelle partie : ---")
            print("Tailles possibles :", VALID_GRID_SIZES)
            print(f"Taille (défaut={user_choices['grid_size']}) : ")
            step = 5

        elif step == 6:
            print(f"Nb bots possibles : 1..55 (défaut={user_choices['num_bots']})")
            print("Nb bots : ")
            step = 7

        elif step == 8:
            print("Niveaux possibles :", VALID_LEVELS)
            print(f"Niveau bots (défaut={user_choices['bot_level']}) : ")
            step = 9

        elif step == 10:
            print("Or au centre ? (oui/non, défaut=non) : ")
            step = 11

        # On lit l'input s’il est dispo (non-bloquant)
        rlist, _, _ = select([sys.stdin], [], [], 0.1)
        if rlist:
            line = sys.stdin.readline().strip()

            # step 1 : choix [1/2/3] => index_terminal_display
            if step == 1:
                if line == "":
                    # Par défaut => 3 => index 2
                    user_choices["index_terminal_display"] = 2
                    print("Aucun choix => on prend le mode Both (GUI+Terminal).")
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
                        print("Mode choisi : Both (GUI+Terminal).")
                else:
                    user_choices["index_terminal_display"] = 2
                    print("Choix invalide => Both (GUI+Terminal).")

                # Prochaine étape => le menu standard
                step = 2

            # step 3 : Choix entre [1] nouvelle partie / [2] charger
            elif step == 3:
                if line == '2':
                    user_choices["load_game"] = True
                    if os.path.isdir(SAVE_DIRECTORY):
                        saves = [f for f in os.listdir(SAVE_DIRECTORY) if f.endswith('.pkl')]
                        if saves:
                            print("Saves disponibles :")
                            for idx, sf in enumerate(saves):
                                print(f"{idx+1} - {sf}")
                            print("Sélection de la sauvegarde : ")
                            step = 12  # on va lire l'index
                        else:
                            print("Aucune sauvegarde valable, on repasse en mode 'nouvelle partie'")
                            user_choices["load_game"] = False
                            step = 4
                    else:
                        print("Pas de répertoire de sauvegarde, on repasse en mode 'nouvelle partie'")
                        user_choices["load_game"] = False
                        step = 4
                else:
                    # On ne fait pas de vérification, on part sur "nouvelle partie"
                    user_choices["load_game"] = False
                    step = 4

            # step 12 : choix de la sauvegarde
            elif step == 12:
                if line == "":
                    print("Pas de saisie => nouvelle partie.")
                    user_choices["load_game"] = False
                    step = 4
                else:
                    try:
                        sel_idx = int(line) - 1
                        if 0 <= sel_idx < len(saves):
                            user_choices["chosen_save"] = os.path.join(SAVE_DIRECTORY, saves[sel_idx])
                            user_choices["validated"] = True
                            print(f"Sauvegarde choisie : {saves[sel_idx]}")
                            return
                        else:
                            print("Index hors liste => nouvelle partie.")
                            user_choices["load_game"] = False
                            step = 4
                    except:
                        print("Choix invalide => nouvelle partie.")
                        user_choices["load_game"] = False
                        step = 4

            # step 5 : saisie taille
            elif step == 5:
                if line == "":
                    print(f"Pas de saisie => taille par défaut {user_choices['grid_size']}")
                    step = 6
                else:
                    if line.isdigit():
                        val = int(line)
                        if val in VALID_GRID_SIZES:
                            user_choices["grid_size"] = val
                            print(f"Taille choisie : {val}")
                    step = 6

            # step 7 : saisie nb bots
            elif step == 7:
                if line == "":
                    print(f"Pas de saisie => nb bots par défaut {user_choices['num_bots']}")
                    step = 8
                else:
                    if line.isdigit():
                        val = int(line)
                        if 1 <= val <= 55:
                            user_choices["num_bots"] = val
                            print(f"Nb bots choisi : {val}")
                    step = 8

            # step 9 : saisie niveau bots
            elif step == 9:
                if line == "":
                    print(f"Pas de saisie => niveau par défaut {user_choices['bot_level']}")
                    step = 10
                else:
                    if line in VALID_LEVELS:
                        user_choices["bot_level"] = line
                        print(f"Niveau bots choisi : {line}")
                    step = 10

            # step 11 : or au centre
            elif step == 11:
                if line == "":
                    print("Pas de saisie => pas d'or au centre (défaut=false).")
                    step = 13
                else:
                    if line.lower() == "oui":
                        user_choices["gold_at_center"] = True
                        print("Or au centre => True.")
                    else:
                        print("Or au centre => False.")
                    step = 13

            # step 13 => validated => on lance la partie
            if step == 13:
                user_choices["validated"] = True
                print("Menu Terminal terminé, on lance la partie.")
                return

        # Petite pause
        time.sleep(0.01)

def main():
    # Init pygame
    screen, screen_width, screen_height = init_pygame()
    load_sprites(screen, screen_width, screen_height)

    # Lance le Terminal en thread
    terminal_thread = threading.Thread(target=ask_terminal_inputs_non_blocking)
    terminal_thread.start()

    # Lance la GUI dans ce thread principal
    run_gui_menu(screen, screen_width, screen_height)

    # Quand la GUI est fermée ou validée, on attend la fin du thread Terminal
    if terminal_thread.is_alive():
        terminal_thread.join()

    # Lecture finale des paramètres
    grid_size     = user_choices["grid_size"]
    number_of_bots= user_choices["num_bots"]
    bot_level     = user_choices["bot_level"]
    gold_at_center= user_choices["gold_at_center"]
    load_game     = user_choices["load_game"]
    chosen_save   = user_choices["chosen_save"]

    # Lance le jeu
    screen, screen_width, screen_height = init_pygame()

    # Si index_terminal_display == 1 => Terminal only => on supprime l'écran => plus de GUI
    if user_choices["index_terminal_display"] == 1:
        screen = None

    if load_game and chosen_save:
        game_map = GameMap(0, False, [], generate=False)
        game_map.load_map(chosen_save)
        print("Carte chargée :", chosen_save)
        players = game_map.players
        game_loop(screen, game_map, screen_width, screen_height, players)
    else:
        players = init_players(number_of_bots, bot_level)
        game_map = GameMap(grid_size, gold_at_center, players)
        game_loop(screen, game_map, screen_width, screen_height, players)


if __name__ == "__main__":
    main()
