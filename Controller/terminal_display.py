import curses
import time
import os

from Controller.terminal_display_debug import debug_print_set_window, debug_print
from Models.Map import GameMap  # si besoin
from Settings.setup import user_choices
from Models.html import write_full_html


def stop_curses():
    curses.endwin()

def start_terminal_interface(game_map):
    """
    Lance le mode curses en parallèle, pour afficher la carte ASCII + zone debug.
    """
    curses.wrapper(_curses_main, game_map)


def _curses_main(stdscr, game_map):
    """
    Fonction principale curses, gère l'affichage ASCII + lecture clavier 
    pour scroller sur la map, etc.
    """
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    # On divise l'écran en 2 : zone map + zone debug
    total_h, total_w = stdscr.getmaxyx()
    debug_h = 5
    map_h = total_h - debug_h

    # Sous-fenêtres
    win_map = curses.newwin(map_h, total_w, 0, 0)
    win_debug = curses.newwin(debug_h, total_w, map_h, 0)
    win_debug.scrollok(True)

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
                    line_chars.append(' ')
                else:
                    entities = game_map.grid.get((map_x, map_y), None)
                    if entities:
                        # On prend la première entité pour l'affichage ASCII
                        e = next(iter(entities))
                        line_chars.append(e.acronym)
                    else:
                        line_chars.append(' ')

            line_str = "".join(line_chars)
            if len(line_str) > width:
                line_str = line_str[:width]

            try:
                win_map.addstr(row, 0, line_str)
            except curses.error:
                pass

        win_map.refresh()

    debug_print("=== Mode curses démarré ===")
    debug_print(f"Map size: {game_map.num_tiles_x} x {game_map.num_tiles_y}")
    debug_print("Tapez ESC pour fermer curses.")

    running = True
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
                time.sleep(0.01)
            # On referme curses
            running = False
            break

        if key != -1:
            # ESC => fermer curses
            if key in [27]:  # 27 = ESC
                running = False
                debug_print("Fermeture curses demandée (ESC).")
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
                saves_folder = 'saves'
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
                            game_map.load_map(os.path.join(saves_folder, chosen_file))
                            debug_print(f"[CURSES] => Chargement réussi: {chosen_file}")
                        except Exception as e:
                            debug_print(f"[CURSES] => Erreur de chargement: {e}")
                        stdscr.nodelay(True)

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
