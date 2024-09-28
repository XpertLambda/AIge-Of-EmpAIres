from Controller.init_map import init_pygame, load_textures, game_loop
from Models.Map import GameMap
from Models.Team import Team
from Controller.init_player import init_players

def main():
    screen = init_pygame()
    textures = load_textures()
    game_map = GameMap()
    game_map.print_map()
    players = init_players(game_map)
    
    game_loop(screen, game_map, textures)


if __name__ == "__main__":
    main()
