from Controller.init_map import *

# Fonction principale pour exécuter le jeu
def main():
    screen = init_pygame()
    textures = load_textures()
    game_map = GameMap(width=MAP_WIDTH, height=MAP_HEIGHT)
    draw_map(screen, game_map, textures)  # Dessiner la carte une seule fois
    game_loop(screen, game_map, textures)  # Lancer la boucle principale

if __name__ == "__main__":
    main()