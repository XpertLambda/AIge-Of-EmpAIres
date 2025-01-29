# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST\Projet_python\Controller\terminal_display.py
import curses
import time
import os

from Controller.terminal_display_debug import debug_print_set_window, debug_print
from Models.Map import GameMap  # si besoin
from Settings.setup import user_choices
from Models.html import write_full_html
from Controller.drawing import generate_team_colors # Importez generate_team_colors depuis drawing.py
from Settings.sync import TEMP_SAVE_PATH

TEMP_SAVE_FILENAME = "temp_save.pkl"

def stop_curses():
    curses.endwin()

def start_terminal_interface(game_map):
    """
    Lance le mode curses en parallèle, pour afficher la carte ASCII + zone debug.
    """
    print("DEBUG: start_terminal_interface called") # DEBUG PRINT
    curses.wrapper(_curses_main, game_map)

def resolve_save_path(relative_path):
    """Helper function to resolve save paths relative to project root"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, relative_path)

def _curses_main(stdscr, game_map):
    """
    Fonction principale curses, gère l'affichage ASCII + lecture clavier
    pour scroller sur la map, etc.
    """
    print("DEBUG: _curses_main started") # DEBUG PRINT
    
    # Reset the terminal completely
    os.system('cls' if os.name == 'nt' else 'clear')
    curses.start_color()
    curses.use_default_colors()
    
    # Initialize curses
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    stdscr.clear()
    stdscr.refresh()

    # Force initial position and redraw
    if not hasattr(game_map, 'terminal_view_x'):
        game_map.terminal_view_x = 0
        game_map.terminal_view_y = 0

    # Force immediate redraw
    total_h, total_w = stdscr.getmaxyx()
    debug_h = 5
    map_h = total_h - debug_h
    win_map = curses.newwin(map_h, total_w, 0, 0)
    win_debug = curses.newwin(debug_h, total_w, map_h, 0)
    
    # Clear both windows explicitly
    win_map.clear()
    win_debug.clear()
    win_map.refresh()
    win_debug.refresh()

    # Définition des codes des touches de fonction
    F9_KEY = 273  # Code standard pour F9 dans curses

    # On divise l'écran en 2 : zone map + zone debug
    total_h, total_w = stdscr.getmaxyx()
    debug_h = 8  # Augmenté de 5 à 8 pour plus de hauteur
    map_h = total_h - debug_h

    # Sous-fenêtres
    win_map = curses.newwin(map_h, total_w, 0, 0)
    win_debug = curses.newwin(debug_h, total_w, map_h, 0)  # Utilise toute la largeur (total_w)
    win_debug.scrollok(True)

    # Move color initialization to a function we can call again when needed
    def init_team_colors():
        curses.start_color()
        team_colors_rgb = generate_team_colors(len(game_map.players))
        team_colors_curses_indices = {}
        start_color_index = 10
        for i, rgb_color in enumerate(team_colors_rgb):
            r, g, b = rgb_color
            curses_r = int(r / 255 * 1000)
            curses_g = int(g / 255 * 1000)
            curses_b = int(b / 255 * 1000)
            curses_color_num = start_color_index + i
            try:
                curses.init_color(curses_color_num, curses_r, curses_g, curses_b)
                curses.init_pair(curses_color_num - start_color_index + 1, curses_color_num, curses.COLOR_BLACK)
                team_colors_curses_indices[i] = curses_color_num - start_color_index + 1
            except curses.error as e:
                debug_print(f"Error initializing color for team {i}: {e}")
                team_colors_curses_indices[i] = 0
        return team_colors_curses_indices

    # Initial color setup
    team_colors_curses_indices = init_team_colors()

    # "Injection" de la fenêtre de debug dans terminal_display_debug.py
    debug_print_set_window(win_debug)

    # On centre la vue curses au départ
    half_map_w = game_map.num_tiles_x // 2
    half_map_h = game_map.num_tiles_y // 2
    game_map.terminal_view_x = max(0, half_map_w - 40)
    game_map.terminal_view_y = max(0, half_map_h - 15)

    def draw_map_portion():
        """
        Dessine la portion visible de la map ASCII dans la fenêtre curses 'win_map'.
        """
        # Recalculer les couleurs avant chaque affichage
        team_colors_curses_indices = init_team_colors()
        
        height, width = win_map.getmaxyx()

        # Calcul des "limites" de défilement
        max_view_x = max(0, game_map.num_tiles_x - width)
        max_view_y = max(0, game_map.num_tiles_y - height)

        tvx = max(0, min(game_map.terminal_view_x, max_view_x))
        tvy = max(0, min(game_map.terminal_view_y, max_view_y))
        game_map.terminal_view_x = tvx
        game_map.terminal_view_y = tvy

        for row in range(height):
            map_y = tvy + row
            if map_y < 0 or map_y >= game_map.num_tiles_y:
                # efface la ligne
                try:
                    win_map.move(row, 0)
                    win_map.clrtoeol()
                except curses.error:
                    pass
                continue

            line_chars = []
            for col in range(width):
                map_x = tvx + col
                if map_x < 0 or map_x >= game_map.num_tiles_x:
                    line_chars.append((' ', 0))
                else:
                    entities = game_map.grid.get((map_x, map_y), None)
                    if entities:
                        # On prend la première entité pour l'affichage ASCII
                        entity = next(iter(entities))
                        acronym = entity.acronym
                        team_id = entity.team
                        if team_id is not None and team_id in team_colors_curses_indices:
                            color_pair_index = team_colors_curses_indices[team_id]
                            line_chars.append((acronym, color_pair_index))
                        else:
                            line_chars.append((acronym, 0)) # Default color if no team or team color not mapped
                    else:
                        line_chars.append((' ', 0))

            line_str = "".join(c[0] for c in line_chars)
            if len(line_str) > width:
                line_str = line_str[:width]

            try:
                win_map.addstr(row, 0, line_str)
                for col_idx, char_data in enumerate(line_chars):
                    char, color_index = char_data
                    if color_index > 0 and char != ' ': # Apply color only for entities and not for space
                        # Utiliser les nouvelles couleurs fraîchement calculées
                        color_pair = team_colors_curses_indices.get(color_index - 1, 0)
                        win_map.chgat(row, col_idx, 1, curses.color_pair(color_pair))
            except curses.error:
                 pass

        win_map.refresh()

    def clear_all_windows():
        """Helper function to aggressively clear all curses windows"""
        # Fill entire windows with spaces
        win_map.bkgd(' ', curses.A_NORMAL)
        win_debug.bkgd(' ', curses.A_NORMAL)
        stdscr.bkgd(' ', curses.A_NORMAL)
        
        # Clear and delete all content
        win_map.clear()
        win_map.erase()
        win_debug.clear()
        win_debug.erase()
        stdscr.clear()
        stdscr.erase()
        
        # Redraw borders if needed
        win_map.box()
        win_debug.box()
        
        # Refresh everything
        win_map.refresh()
        win_debug.refresh()
        stdscr.refresh()

    def clear_and_reset_curses(stdscr, win_map, win_debug, team_colors_curses_indices):
        """Helper function to properly clear and reset curses windows"""
        try:
            # 1. Reset complet des couleurs d'abord
            curses.start_color()
            curses.use_default_colors()
            
            # 2. Réinitialisation agressive de toutes les paires de couleurs
            for i in range(1, curses.COLORS):
                try:
                    curses.init_pair(i, -1, -1)
                except:
                    pass
                    
            # 3. Clear agressif des fenêtres
            for win in [stdscr, win_map, win_debug]:
                win.clear()
                win.erase()
                win.refresh()
                # Remplir explicitement avec des espaces
                h, w = win.getmaxyx()
                for y in range(h):
                    try:
                        win.addstr(y, 0, " " * w)
                    except curses.error:
                        pass
                # Reset des attributs
                win.attrset(curses.A_NORMAL)
                win.bkgd(' ', curses.A_NORMAL)
                
            # 4. Régénérer complètement les nouvelles couleurs
            team_colors_curses_indices = init_team_colors()
            
            # 5. Forcer un refresh complet
            stdscr.noutrefresh()
            win_map.noutrefresh()
            win_debug.noutrefresh()
            curses.doupdate()
            
            time.sleep(0.1)  # Petit délai pour s'assurer que tout est appliqué
            
            return team_colors_curses_indices
                
        except curses.error as e:
            debug_print(f"Error during curses reset: {e}")
            return init_team_colors()  # En cas d'erreur, on retourne quand même de nouvelles couleurs

    debug_print("=== Mode curses démarré ===")
    debug_print(f"Map size: {game_map.num_tiles_x} x {game_map.num_tiles_y}")
    debug_print("Tapez ESC pour fermer curses.")

    running = True

    # Ajouter le compteur de tentatives pour la détection du fichier temp
    check_temp_counter = 0

    while running:
        try:
            key = stdscr.getch()
        except:
            key = -1

        # -- Fin de partie ? --
        if game_map.game_state and game_map.game_state.get('game_over', False):
            # On affiche un message global
            debug_print("=== GAME OVER ===")
            debug_print("[M] Menu principal | [Q] Quitter")

            # Ici on attend un choix bloquant => on enlève le nodelay
            stdscr.nodelay(False)
            chosen = None
            while chosen is None:
                c = stdscr.getch()
                if c in [ord('m'), ord('M')]:
                    user_choices["menu_result"] = "main_menu"
                    chosen = 'm'
                elif c in [ord('q'), ord('Q')]:
                    user_choices["menu_result"] = "quit"
                    chosen = 'q'
                time.sleep(0.005)
            # On referme curses
            running = False
            break

        if key != -1:
            # ESC => fermer curses
            if key in [27]:  # 27 = ESC
                running = False
                debug_print("Fermeture curses demandée (ESC).")
                break

            # F9 => switch display mode (curses <-> GUI)
            elif key in [F9_KEY, curses.KEY_F9]:  # On teste les deux codes possibles
                from Settings.setup import user_choices
                if user_choices["index_terminal_display"] in [0, 1]:
                    debug_print("[CURSES] F9 => Switch display mode requested")
                    if game_map.game_state:
                        game_map.game_state['switch_display'] = True
                    user_choices["menu_result"] = "switch_display"
                    running = False

                    # Nettoyer l'écran avant de sortir
                    stdscr.clear()
                    win_map.clear()
                    win_debug.clear()
                    stdscr.refresh()
                    win_map.refresh()
                    win_debug.refresh()

                    break

            move_amount = 1

            if key in [ord('Z'), ord('S'), ord('Q'), ord('D')]:
                move_amount = 2

            if key == curses.KEY_UP or key == ord('z') or key == ord('Z'):
                game_map.terminal_view_y -= move_amount
            elif key == curses.KEY_DOWN or key == ord('s') or key == ord('S'):
                game_map.terminal_view_y += move_amount
            elif key == curses.KEY_LEFT or key == ord('q') or key == ord('Q'):
                game_map.terminal_view_x -= move_amount
            elif key == curses.KEY_RIGHT or key == ord('d') or key == ord('D'):
                game_map.terminal_view_x += move_amount

            elif key == ord('m'):
                debug_print("[CURSES] touche 'm' => recentrer la vue curses")
                half_w = game_map.num_tiles_x // 2
                half_h = game_map.num_tiles_y // 2
                game_map.terminal_view_x = max(0, half_w - 40)
                game_map.terminal_view_y = max(0, half_h - 15)

            # 5) Touche Tab => pause/unpause + snapshot
            elif key == 9:  # ASCII 9 = TAB
                if game_map.game_state is not None:
                    is_paused = not game_map.game_state.get('paused', False)
                    game_map.game_state['paused'] = is_paused
                    if is_paused:
                        if hasattr(game_map, 'players'):
                            write_full_html(game_map.players, game_map)
                        debug_print("[CURSES] Tab => Pause ON + snapshot générée")
                    else:
                        debug_print("[CURSES] Tab => Unpause => reprise du jeu")

            elif key == ord('p'):
                if game_map.game_state is not None:
                    is_paused = not game_map.game_state.get('paused', False)
                    game_map.game_state['paused'] = is_paused
                    if is_paused:
                        debug_print("[CURSES] 'p' => Pause ON")
                    else:
                        debug_print("[CURSES] 'p' => Unpause => reprise du jeu")

            # 6) Touche k => Sauvegarde
            elif key in [ord('k'), ord('K')]:
                debug_print("[CURSES] K => Sauvegarde en cours...")
                game_map.save_map()
                debug_print("[CURSES] => Sauvegarde effectuée !")

            # 7) Touche L => Chargement
            elif key in [ord('l'), ord('L')]:
                debug_print("[CURSES] L => Chargement. Listing saves...")
                saves_folder = resolve_save_path('saves')
                if not os.path.isdir(saves_folder):
                    debug_print("[CURSES] => Pas de dossier 'saves'")
                else:
                    save_files = [f for f in os.listdir(saves_folder) if f.endswith('.pkl')]
                    if not save_files:
                        debug_print("[CURSES] => Aucune sauvegarde disponible")
                    else:
                        for i, sf in enumerate(save_files):
                            debug_print(f"{i}: {sf}")
                        debug_print("[CURSES] Entrez le numéro de la save (puis Entrée):")
                        stdscr.nodelay(False)
                        try:
                            num_str = stdscr.getstr().decode('utf-8')
                            choice_idx = int(num_str)
                            chosen_file = save_files[choice_idx]
                            save_path = os.path.join(saves_folder, chosen_file)
                            
                            # Charger la nouvelle save
                            game_map.load_map(save_path)
                            
                            # Clear et reset propre de curses
                            team_colors_curses_indices = clear_and_reset_curses(stdscr, win_map, win_debug, team_colors_curses_indices)
                            
                            # Sauvegarder pour la GUI
                            game_map.save_map(TEMP_SAVE_PATH)
                            
                            debug_print(f"[CURSES] => Loaded save: {chosen_file}")
                            debug_print("[CURSES] => Created temp save for GUI sync")
                        except Exception as e:
                            debug_print(f"[CURSES] => Error during load/sync: {e}")
                        stdscr.nodelay(True)

        # If GUI loaded a save and set force_sync => reload here
        if game_map.game_state.get('force_sync'):
            if os.path.exists(TEMP_SAVE_FILENAME):
                game_map.load_map(TEMP_SAVE_FILENAME)
                # Reset force_sync so we don't reload forever
                game_map.game_state['force_sync'] = False

        # Vérifier plus fréquemment l'existence du fichier temp
        check_temp_counter += 1
        if check_temp_counter >= 10:  # Vérifier toutes les 10 itérations
            check_temp_counter = 0
            from Controller.sync_manager import check_and_load_sync
            if check_and_load_sync(game_map):
                debug_print("[CURSES] Sync state loaded")
                # Réinitialiser les couleurs
                team_colors_curses_indices = init_team_colors()
            if os.path.exists(TEMP_SAVE_PATH):
                try:
                    debug_print("[CURSES] Found temp save, reloading for sync...")
                    
                    # Clear et reset propre avant chargement
                    team_colors_curses_indices = clear_and_reset_curses(stdscr, win_map, win_debug, team_colors_curses_indices)
                    
                    game_map.load_map(TEMP_SAVE_PATH)
                    
                    # Recalculer explicitement les couleurs après chargement
                    team_colors_curses_indices = init_team_colors()
                    
                    debug_print("[CURSES] Temp save loaded successfully")
                    
                    os.remove(TEMP_SAVE_PATH)
                except Exception as e:
                    debug_print(f"[CURSES] Error loading temp save: {e}")
                    if os.path.exists(TEMP_SAVE_PATH):
                        os.remove(TEMP_SAVE_PATH)  # Nettoyer même en cas d'erreur

        # Redraw
        win_map.erase()
        draw_map_portion()

        if game_map.game_state is not None:
            if not game_map.game_state.get('paused', False):
                game_map.patch(0.005)
        else:
            game_map.patch(0.005)

        time.sleep(0.005)

    debug_print("=== Fin mode curses ===")