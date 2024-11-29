
#from Models.Team import Team
#from Models.Map import *
from math import sqrt
import time
from Models import Building

def dist(x1,y1,x2,y2):
        return sqrt((x1-x2)**2 + (y1-y2)**2)


class Unit():
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
        self.direction=0 #8 direction: 0(vers la droite), 45, 90, 135, 180, 225, 270, 315.
        self.current_frame=0
        self.frame_counter=0
        self.frame_duration=2
        self.task=False
        self.id=Unit.cpt
        Unit.cpt+=1
    

    def attaquer(self,cible,map):
        self.current_frame=0
        self.frame_counter=0
        #print("attaque 1")
        while(cible.hp!=0 and self.hp !=0):
            #time.sleep(self.speed)
            if dist(self.x,self.y,cible.x,cible.y)<2:
                #print("c", cible.hp)
                cible.hp-=self.attack
            else:
                return False
        return True
                
    def search(self,t0,t,map):
        print("deb",self.id)
        current_hp=self.hp
        while(self.hp>0 and t.buildings!=[] and t.army!=[]):
            #while(current_hp==self.hp):
            time.sleep(2)
            min=300000
            """
            for b in t.buildings:
                distance=dist(b.x,b.y,self.x,self.y)
                if(distance<min):
                    min=distance
                    e=b
            """
            print("army",len(t.army),self.id)
            for u in t.army:
                distance=dist(u.x,u.y,self.x,self.y)
                if(distance<min):
                    min=distance
                    e=u
            b=False
            print("army",len(t.army),e.id,self.id)
            while(not(b)):
                b=self.attaquer(e,map)
                self.SeDeplacer(e.x,e.y,map)
            if e.hp<=0:
                if e in t.buildings:
                    t.buildings.remove(e)
                elif e in t.army:
                    t.army.remove(e)
        #if self.hp==0:
        #    t0.army.remove(self)
        print("fin",self.id)

    

    
    def SeDeplacer(self,x,y,map):
        self.frame_counter=0
        self.current_frame=0
        while(self.x!=x and self.y!=y):

            time.sleep(self.speed)
            if self.x<x:
                if self.y<y and map.grid[y+1][x+1].is_walkable:
                    self.x+=1
                    self.y+=1
                    self.direction=270
                if self.y>y and map.grid[y-1][x+1].is_walkable:
                    self.x+=1
                    self.y-=1
                    self.direction=90
                if map.grid[y][x+1].is_walkable:
                    self.x+=1
                    self.direction=135
            if self.x>x:
                if self.y<y and map.grid[y+1][x+1].is_walkable:
                    self.x-=1
                    self.y+=1
                if self.y>y and map.grid[y-1][x+1].is_walkable:
                    self.x-=1
                    self.y-=1
                    self.direction=90
                if map.grid[y][x+1].is_walkable:
                    self.x-=1
                    self.direction=315
            if self.y<y and map.grid[y+1][x].is_walkable:
                self.y+=y
                self.direction=225
            if self.y>y and map.grid[y-1][x].is_walkable:
                self.y-=y
                self.direction=45
            
                

    def work(self):
        tps=time.clock_gettime(time.CLOCK_REALTIME)
        while(not(self.task)):
            if time.clock_gettime(time.CLOCK_REALTIME-tps)>=5.5:
                self.task=True
                return True
        
       
