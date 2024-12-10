#from Models.Team import Team
from Models.Map import *
from math import sqrt
import random
import time
from Entity.Entity import *
from Settings.setup import *
from Controller.isometric_utils import *
from Controller.init_sprites import draw_sprite

class Unit(Entity):
    cpt=0
    def __init__(self, x, y, team, acronym, cost_food, cost_gold, cost_wood, hp, attack, speed, training_time):
        super().__init__(x, y, team, acronym, size=1)

        self.cost_food = cost_food
        self.cost_gold = cost_gold
        self.cost_wood = cost_wood
        self.hp = hp
        self.max_hp = self.hp  # ajout
        self.attack = attack
        self.speed = speed
        self.training_time = training_time
        self.task="nothing"
        self.id=Unit.cpt
        Unit.cpt+=1

        self.state = random.randint(0, 3)
        self.frames = FRAMES_PER_UNIT
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_duration = 3
        self.direction = 0

    @staticmethod
    def dist(x1,y1,x2,y2):
        return sqrt((x1-x2)**2 + (y1-y2)**2)

    def attaquer(self,att,t,map):
        b=True
        if(self.cible == None or self.cible.hp==0):
            b=self.search(t,att)
        if b:
            if dist(self.x,self.y,self.cible.x,self.cible.y)<100:
                self.current_frame=0
                self.frame_counter=0
                self.cible.hp-=self.attack
                cible.notify_damage()  # éventuellement notifier les dommages ici
            else:
                self.SeDeplacer(self.cible.x,self.cible.y,map)
        return b
    
    def search(self,t,att):
        min=300000
        e=None
        for u in t.army:
            distance=dist(u.x,u.y,self.x,self.y)
            if(att or distance<100):
                if(distance<min):
                    min=distance
                    e=u         
        if att:
            for b in t.buildings:
                print("b=",b)
                distance=dist(b.x,b.y,self.x,self.y)
                if(distance<min):
                    min=distance
                    e=b
 
        self.cible=e
    
    def SeDeplacer(self,x,y,map):
        #deplacement seulement d'une tile
        self.frame_counter=0
        self.current_frame=0
        if(self.x!=x and self.y!=y):
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
       

    def display(self, screen, screen_width, screen_height, camera):
        category = 'units'
        self.frame_counter += 1
        if self.frame_counter >= self.frame_duration:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % self.frames
        screen_x, screen_y = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, category, screen_x, screen_y, camera.zoom, self.team, self.state, self.current_frame)
