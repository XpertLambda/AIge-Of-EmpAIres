# Chemin : /home/cyril/Documents/Projet_python/Controller/terminal_display_debug.py

import curses

_debug_window = None

def debug_print_set_window(win):
    """
    Permet à 'terminal_display.py' de nous transmettre la window curses
    utilisée pour afficher les messages de debug.
    """
    global _debug_window
    _debug_window = win

def debug_print(msg):
    """
    Méthode globale pour que d'autres modules puissent afficher
    des messages de debug dans la zone debug curses.
    """
    global _debug_window
    if _debug_window is None:
        # Si pas encore initialisé => on ne fait rien
        return

    # On scrolle d'une ligne
    _debug_window.scroll(1)
    # On tronque si trop long
    max_y, max_x = _debug_window.getmaxyx()
    msg = msg[:max_x-1]

    try:
        _debug_window.addstr(max_y - 1, 0, msg)
    except curses.error:
        pass

    _debug_window.refresh()
