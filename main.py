# main.py
import pygame  # Ensure pygame is imported here
from Controller.init_map import init_pygame, game_loop
from Models.Map import GameMap
from Models.Team import Team
from Controller.init_player import init_players
from Controller.init_sprites import load_sprites
from Settings.setup import NUMBER_OF_PLAYERS
from Entity.Building.Barracks import Barracks

def main():
    # Déballer les retours de init_pygame
    screen, screen_width, screen_height = init_pygame()
    players = init_players(NUMBER_OF_PLAYERS)
    load_sprites()
    # Initialiser la carte de jeu
    game_map = GameMap(players)
    game_map.print_map()
    # Lancer la boucle de jeu avec tous les arguments requis
    game_loop(screen, game_map, screen_width, screen_height, players)  
    print("ok")
    t=Team("lean",1)
    t1=Team("lean",2)
    t.resources["food"]=10000
    t1.resources["food"]=10000
    b=Barracks(t)
    t.units=[]
    t1.units=[]
    b.entraine(t,0)
    b.entraine(t1,0)
    b.entraine(t,0)
    for i in range(0,10):
        t.battle(t1,game_map,2)
        t.gestion()
        t1.gestion()
        for i in range(0,len(t.units)):
            print(i,"hp",t.units[i].hp)
            t.units[i].task=False
        for i in range(0,len(t1.units)):
            print(i,"hp2",t1.units[i].hp)
            t1.units[i].task=False
    print("ok")

if __name__ == "__main__":
    main()