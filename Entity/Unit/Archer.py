from Models.Resources import Resources
import math
import pygame
import random
from AiUtils.aStar import a_star
from Entity.Entity import Entity
from Entity.Unit import Unit
from Entity.Building import Building
from Settings.setup import FRAMES_PER_UNIT, HALF_TILE_SIZE,TILE_SIZE, ALLOWED_ANGLES, ATTACK_RANGE_EPSILON, UNIT_HITBOX
from Controller.utils import tile_to_screen, get_direction, get_snapped_angle, normalize
from Controller.drawing import draw_sprite, draw_hitbox, draw_path
from Projectile.Arrow import *

class Archer(Unit):
    def __init__(self, team=None, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym="a",
            max_hp=30,
            cost=Resources(food=0, gold=45, wood=25),
            attack_power=4,
            attack_range=4,
            attack_speed=2.03,
            speed=1,
            training_time=35
        )

        self.threw = False

    def seekAttack(self, game_map, dt):
        self.range_color = (255, 255, 255)
        if self.attack_target and self.attack_target.isAlive():
            if isinstance(self.attack_target, Unit):
                distance = math.dist((self.x, self.y), (self.attack_target.x, self.attack_target.y))
                distance -= (self.attack_target.hitbox + self.attack_range)
            else:
                corner_distance = self.attack_target.size / 2.0
                left = self.attack_target.x - corner_distance
                right = self.attack_target.x + corner_distance
                top = self.attack_target.y - corner_distance
                bottom = self.attack_target.y + corner_distance
                closest_point = (
                    max(left, min(self.x, right)),
                    max(top, min(self.y, bottom))
                )
                distance = math.dist(closest_point, (self.x, self.y)) - self.attack_range          
            if distance <= 0 :
                self.state = 'attack'
                self.direction = get_direction(get_snapped_angle((self.x, self.y), (self.attack_target.x, self.attack_target.y))) 
                if self.attack_timer == 0:
                    self.threw = False
                    self.current_frame = 0
                    self.path = []
                
                elif self.current_frame == self.frames - 1:
                    self.cooldown_frame = self.current_frame
                
                if self.attack_timer >= self.attack_speed/3 and not self.threw:
                    self.threw = True
                    arrow = Arrow(self, self.attack_target)
                    arrow.launch(game_map, z_launch=1.5)

                self.attack_timer += dt
                if self.attack_timer >= self.attack_speed:
                    self.attack_timer = 0
                    self.cooldown_frame = None

            else :
                self.hitbox_color = (255, 255, 255)
                self.attack_target.hitbox_color = (255, 255, 255)
                if isinstance(self.attack_target, Unit):
                    if self.path:
                        self.path = [self.path[0]] + a_star((self.x, self.y), (self.attack_target.x,self.attack_target.y), game_map)
                    else:
                        self.set_destination((self.attack_target.x,self.attack_target.y), game_map)
                else:
                    if not self.path:
                        self.set_destination((self.attack_target.x,self.attack_target.y), game_map)

                self.attack_timer = 0
        else: 
            self.attack_target = None