from Controller.init_map import init_pygame, load_textures, game_loop
from Models.Map import GameMap
from Models.Team import Team
from Controller.init_player import init_players
from Settings.setup import NUMBER_OF_PLAYERS

def main():
    #screen = init_pygame()
    textures = load_textures()
    players = init_players(NUMBER_OF_PLAYERS)
    game_map = GameMap(players)
    game_map.print_map()
    
    #game_loop(screen, game_map, textures)


if __name__ == "__main__":
    main()
