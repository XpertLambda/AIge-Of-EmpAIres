from Controller.init_map import init_pygame, load_textures, game_loop
from Models.Map import GameMap
from Models.Team import Team
from Controller.init_player import init_players
from Models.Unit.Swordsman import *
from Models.Building.Barracks import Barracks
from Models.Building.ArcheryRange import ArcheryRange
from Models.Building.Stable import Stable

def main():
    #screen = init_pygame()
    textures = load_textures()
    game_map = GameMap()
    #game_map.print_map()
    players = init_players(game_map)
    b=Barracks()

    s1=b.entraine()
    s2=b.entraine()
    #s1.SeDeplacer(2,2,game_map)
    s1.attaquer(s2)

    print(s2.hp,"ok")
    #game_loop(screen, game_map, textures)

    ###TEST HTML###
    t=Team("lean")
    t.army.add(s1)
    t.army.add(s2)
    t.write_html()


if __name__ == "__main__":
    main()
