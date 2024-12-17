# Entity/Unit/Unit.py
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
        self.max_hp = self.hp
        self.attack = attack
        self.speed = speed
        self.training_time = training_time
        self.task = "nothing"
        self.id = Unit.cpt
        Unit.cpt += 1

        self.state = random.randint(0, 3)
        self.frames = FRAMES_PER_UNIT
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_duration = 3
        self.direction = 0

        self.cible = None  # Définir la cible par défaut à None

    @staticmethod
    def dist(x1,y1,x2,y2):
        return sqrt((x1-x2)**2 + (y1-y2)**2)

    def attaquer(self,att,t,map):
        b=True
        if(self.cible is None or self.cible.hp == 0):
            b = self.search(t,att)
        if b and self.cible is not None:
            if Unit.dist(self.x,self.y,self.cible.x,self.cible.y)<100:
                self.current_frame=0
                self.frame_counter=0
                self.cible.hp-=self.attack
                self.cible.notify_damage()  # utiliser self.cible au lieu de cible
            else:
                self.SeDeplacer(self.cible.x,self.cible.y,map)
        return b
    
    def search(self,t,att):
        min_dist=300000
        e=None
        # On utilise Unit.dist
        for u in t.army:
            distance=Unit.dist(u.x,u.y,self.x,self.y)
            if(att or distance<100):
                if(distance<min_dist):
                    min_dist=distance
                    e=u         
        if att:
            for b in t.buildings:
                distance=Unit.dist(b.x,b.y,self.x,self.y)
                if(distance<min_dist):
                    min_dist=distance
                    e=b
        self.cible=e
        return e is not None
    
    def is_tile_walkable(self, map, x, y):
        # Vérifier que la case (x,y) est dans la grille
        if x < 0 or y < 0 or x >= map.num_tiles_x or y >= map.num_tiles_y:
            return False
        pos = (x,y)
        if pos not in map.grid:
            # Pas d'entité ici, donc c'est walkable (terrain "vide" ?)
            # S'il faut un sol, le code doit le gérer.
            return True
        # S'il y a des entités, vérifier si au moins l'une n'est pas walkable
        for ent in map.grid[pos]:
            if hasattr(ent, 'is_walkable') and not ent.is_walkable():
                return False
        return True

    def SeDeplacer(self,x,y,map):
        # Déplacement d'une tile. On doit vérifier la walkabilité.
        self.frame_counter=0
        self.current_frame=0

        target_x = int(x)
        target_y = int(y)

        # Exemple simplifié : on tente un déplacement d'une step vers la direction voulue.
        # On check toutes les directions isométriques possibles.
        # Note : le code actuel est rudimentaire et doit être amélioré.
        # On vérifie la présence d'entités avec is_tile_walkable().

        dx = 0
        dy = 0
        if self.x < target_x:
            dx = 1
        elif self.x > target_x:
            dx = -1
        if self.y < target_y:
            dy = 1
        elif self.y > target_y:
            dy = -1

        # Essai de déplacement diagonal si possible
        if dx != 0 and dy != 0:
            if self.is_tile_walkable(map, int(self.x+dx), int(self.y+dy)):
                self.x += dx
                self.y += dy
                # Ajuster direction en fonction dx/dy
                if dx==1 and dy==1:
                    self.direction=270
                elif dx==1 and dy==-1:
                    self.direction=90
                elif dx==-1 and dy==1:
                    self.direction=225
                elif dx==-1 and dy==-1:
                    self.direction=45
                return

        # Essai de déplacement horizontal si pas diagonal possible
        if dx != 0:
            if self.is_tile_walkable(map, int(self.x+dx), int(self.y)):
                self.x += dx
                # Ajuster direction
                if dx==1:
                    self.direction=135
                else:
                    self.direction=315
                return

        # Essai de déplacement vertical si horizontal pas possible
        if dy != 0:
            if self.is_tile_walkable(map, int(self.x), int(self.y+dy)):
                self.y += dy
                if dy==1:
                    self.direction=225
                else:
                    self.direction=45

    def display(self, screen, screen_width, screen_height, camera):
        category = 'units'
        self.frame_counter += 1
        if self.frame_counter >= self.frame_duration:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % self.frames
        screen_x, screen_y = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, category, screen_x, screen_y, camera.zoom, self.state, self.current_frame)
