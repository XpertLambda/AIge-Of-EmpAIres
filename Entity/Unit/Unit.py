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

    def attaquer(self,cible):
        if self.dist(self.x,self.y,cible.x,cible.y)<2:
            cible.hp-=self.attack
            cible.notify_damage()  # éventuellement notifier les dommages ici
            return True
        return False

    def SeDeplacer(self,x,y,map):
        while(self.x!=x and self.y!=y):
            # La logique de déplacement reste inchangée
            if self.x<x:
                if self.y<y and map.grid[(x+1, y+1)].is_walkable():
                    self.x+=1
                    self.y+=1
                elif self.y>y and map.grid[(x+1, y-1)].is_walkable():
                    self.x+=1
                    self.y-=1
            if self.x>x:
                if self.y<y and map.grid[(x-1, y+1)].is_walkable():
                    self.x-=1
                    self.y+=1
                elif self.y>y and map.grid[(x-1, y-1)].is_walkable():
                    self.x-=1
                    self.y-=1
            if self.x==x:
                if self.y<y and map.grid[(x, y+1)].is_walkable():
                    self.y+=1
                elif self.y>y and map.grid[(x, y-1)].is_walkable():
                    self.y-=1
            if self.y==y:
                if self.x<x and map.grid[(x+1, y)].is_walkable():
                    self.x+=1
                elif self.x>x and map.grid[(x-1, y)].is_walkable():
                    self.x-=1

    def display(self, screen, screen_width, screen_height, camera):
        category = 'units'
        self.frame_counter += 1
        if self.frame_counter >= self.frame_duration:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % self.frames
        screen_x, screen_y = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, category, screen_x, screen_y, camera.zoom, self.team, self.state, self.current_frame)
