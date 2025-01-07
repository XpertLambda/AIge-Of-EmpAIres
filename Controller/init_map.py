import sys
import pygame
from Models.Map import GameMap
from Models.Team import Team
from Settings.setup import WINDOW_WIDTH, WINDOW_HEIGHT
from Controller.game_loop import game_loop
from Controller.init_player import init_players

def init_pygame():
    pygame.init()
    pygame.display.set_caption("Age of Empires II - Version Python")

    # Fenêtre directement maximisée.
    screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE | pygame.WINDOWMAXIMIZED)
    screen_width, screen_height = screen.get_width(), screen.get_height()

    pygame.event.post(
        pygame.event.Event(
            pygame.VIDEORESIZE,
            {
                "size": (screen_width, screen_height),
                "w": screen_width,
                "h": screen_height
            }
        )
    )

    return screen, screen_width, screen_height


if __name__ == "__main__":
    grid_size = int(input("Veuillez entrer la taille de la grille : "))
    number_of_players = int(input("Veuillez entrer le nombre de joueurs : "))
    gold_at_center_input = input("Voulez-vous de l'or au centre ? (oui/non) : ").lower()
    gold_at_center = gold_at_center_input == 'oui'

    screen, screen_width, screen_height = init_pygame()
    game_map = GameMap(grid_size, gold_at_center)
    players = init_players(number_of_players)
    game_loop(screen, game_map, screen_width, screen_height, players)
