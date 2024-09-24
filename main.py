from Controller.init_map import *

# Fonction principale pour exécuter le jeu
def main():
    screen = init_pygame()
    textures = load_textures()
    game_map = GameMap()
    game_map.print_map()
    game_loop(screen, game_map, textures)

if __name__ == "__main__":
    main()