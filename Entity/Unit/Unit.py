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

        self.cost_food = cost_food  # Coût en nourriture
        self.cost_gold = cost_gold  # Coût en or
        self.cost_wood = cost_wood  # Coût en bois
        self.hp = hp              # Points de vie
        self.attack = attack      # Attaque
        self.speed = speed        # Vitesse (en tuiles/seconde)
        self.training_time = training_time  # Temps d'entraînement (en secondes)
        self.task="nothing"
        self.id=Unit.cpt
        Unit.cpt+=1

        self.state = random.randint(0, 3)# Current animation type
        #DEBUG : 
        self.frames = FRAMES_PER_UNIT
        self.current_frame = 0
        self.frame_counter = 0  
        self.frame_duration = 3 
        self.direction = 0
    

    def attaquer(self,cible):
        if dist(self.x,self.y,cible.x,cible.y)<2:
            cible.hp-=self.attack
            return True
        return False

    def dist(x1,y1,x2,y2):
        return sqrt((x1-x2)**2 + (y1-y2)**2)
    
    def SeDeplacer(self,x,y,map):
        while(self.x!=x and self.y!=y):

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
            if self.x==x:
                if self.y<y and map.grid[y+1][x].is_walkable:
                    self.y+=1
                if self.y>y and map.grid[y-1][x].is_walkable:
                    self.y-=1
            if self.y==y:
                if self.x<x and map.grid[y][x+1].is_walkable:
                    self.x+=1
                if self.x>x and map.grid[y][x-1].is_walkable:
                    self.x-=1

    def display(self, screen, screen_width, screen_height, camera):
        category = 'units'
        # Update frame for animation
        self.frame_counter += 1
        if self.frame_counter >= self.frame_duration:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % self.frames
        # Draw the current frame of the animation
        screen_x, screen_y = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, category, screen_x, screen_y, camera.zoom, self.team, self.state, self.current_frame)
