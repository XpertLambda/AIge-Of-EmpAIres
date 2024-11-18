# main.py

from Controller.init_map import init_pygame, game_loop
from Models.Map import GameMap
from Models.Team import Team
from Controller.init_player import init_players
from Settings.setup import NUMBER_OF_PLAYERS
from Models.Unit.Swordsman import *
from Models.Building.Barracks import Barracks
from Models.Building.ArcheryRange import ArcheryRange
from Models.Building.Stable import Stable
import time
import threading


def main():
    tps1=time.clock_gettime(time.CLOCK_REALTIME)
    b=Barracks()
    t=Team("lean")
    thread1=threading.Thread(target=b.entraine(t))
    thread1.start()
    thread2=threading.Thread(target=b.entraine(t))
    thread2.start()
    thread1.join()
    thread2.join()
    threading.Thread(target=t.soldats[0].attaquer(t.soldats[1]))
    

    ###TEST HTML###
    
    print(t.builds(False,"B"))
    tps2=time.clock_gettime(time.CLOCK_REALTIME)
    print(tps2-tps1)
    #t.write_html()
    print("fin")


     # Déballer les retours de init_pygame
    screen, screen_width, screen_height = init_pygame()
    players = init_players(NUMBER_OF_PLAYERS)

    # Initialiser la carte de jeu
    game_map = GameMap(players)
    #game_map.print_map()  
    
    # Lancer la boucle de jeu avec tous les arguments requis
    game_loop(screen, game_map, screen_width, screen_height, players)  
 


if __name__ == "__main__":
    main()