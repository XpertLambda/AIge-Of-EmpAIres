from Models.Team import Team


#from Models.Team import Team
from Models.Map import *
from math import sqrt
import time

def dist(x1,y1,x2,y2):
        return sqrt((x1-x2)**2 + (y1-y2)**2)


class Unit(Team):
    cpt=0
    def __init__(self, acronym, cost_food, cost_gold, cost_wood, hp, attack, speed, training_time,x=0,y=0):
        self.acronym = acronym          # Nom de l'unité (Villager, Swordsman, etc.)
        self.cost_food = cost_food  # Coût en nourriture
        self.cost_gold = cost_gold  # Coût en or
        self.cost_wood = cost_wood  # Coût en bois
        self.hp = hp              # Points de vie
        self.attack = attack      # Attaque
        self.speed = speed        # Vitesse (en tuiles/seconde)
        self.training_time = training_time  # Temps d'entraînement (en secondes)
        #position
        self.x=x
        self.y=y
        self.task="nothing"
        self.id=Unit.cpt
        Unit.cpt+=1
    

    def attaquer(self,cible):
        if dist(self.x,self.y,cible.x,cible.y)<2:
            cible.hp-=self.attack
            return True
        return False
    
    def SeDeplacer(self,x,y,map):
        while(self.x!=x and self.y!=y):

            time.sleep(self.speed)
            if self.x<x:
                if self.y<y and map.grid[y+1][x+1].is_walkable:
                    self.x+=1
                    self.y+=1
                if self.y>y and map.grid[y-1][x+1].is_walkable:
                    self.x+=1
                    self.y-=1
            if self.x>x:
                if self.y<y and map.grid[y+1][x+1].is_walkable:
                    self.x-=1
                    self.y+=1
                if self.y>y and map.grid[y-1][x+1].is_walkable:
                    self.x-=1
                    self.y-=1
       
       
