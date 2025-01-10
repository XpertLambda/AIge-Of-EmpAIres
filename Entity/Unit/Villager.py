import math
import pygame
from Settings.setup import RESOURCE_CAPACITY, RESOURCE_COLLECTION_RATE, Resources, FRAMES_PER_UNIT, HALF_TILE_SIZE,TILE_SIZE, ALLOWED_ANGLES, ATTACK_RANGE_EPSILON, UNIT_HITBOX
from Entity.Resource.Resource import Resource
from Entity.Unit.Unit import Unit
from Entity.Entity import Entity
from Entity.Building import Building
from AiUtils.aStar import a_star
from Controller.isometric_utils import get_direction, get_snapped_angle

class Villager(Unit):
    def __init__(self, team=None, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym="v", 
            max_hp=40, 
            cost=Resources(food=50, gold=0, wood=25), 
            attack_power=2,
            attack_range=1, 
            attack_speed=2.03,
            speed=1, 
            training_time=20, 

        )
        self.resources = Resources(food=0, gold=0, wood=0)
        self.carry_capacity = RESOURCE_CAPACITY
        self.resource_rate = RESOURCE_COLLECTION_RATE / 60
        self.task = None

    # ---------------- Update Unit ---------------
    def update(self, game_map, dt):
        if self.isAlive():
            self.setIdle()
            self.seekAttack(game_map, dt)
            self.seekCollision(game_map, dt)
            self.seekMove(game_map, dt)
            #self.seekCollect(game_map, dt)
            #self.seekStock(game_map, dt)
            #self.seekBuild(game_map, dt)
        else:
            self.death(game_map, dt)

    # ---------------- Controller ----------------
    def set_target(self, target):
        if target and target.team != None and target.isAlive() and target.entity_id != self.entity_id and target.team != self.team:
            self.target = target
            return
        self.target = None

    def seekAttack(self, game_map, dt):
        if self.target and self.isAvailable() and self.target.isAlive():
            distance = math.dist((self.x, self.y), (self.target.x, self.target.y)) - self.target.hitbox - self.attack_range

            if distance <= 0 :
                self.state = 2
                self.direction = get_direction(get_snapped_angle((self.x, self.y), (self.target.x, self.target.y))) 
                if self.attack_timer == 0:
                    self.current_frame = 0
                    self.path = []
                
                elif self.current_frame == self.frames - 1:
                    self.cooldown_frame = self.current_frame
                    
                self.attack_timer += dt
                if self.attack_timer >= self.attack_speed:
                    self.target.hp -= self.attack_power
                    self.attack_timer = 0
                    self.cooldown_frame = None
            else :
                if self.path:
                    self.path = [self.path[0]] + a_star(self, (round(self.target.x), round(self.target.y)), game_map)
                else:
                    self.path = a_star(self, (round(self.target.x), round(self.target.y)), game_map)

                self.attack_timer = 0

    def isAvailable(self):
        return not self.task


    '''
    def collectResource(self, resource_tile, duration, game_map):
        if not self.isAvailable():
            return
        if not isinstance(resource_tile, Resource):
            return
        self.task = 'collect'
        self.move(resource_tile.x, resource_tile.y, game_map)
        collected = min(
            self.resource_rate * duration,
            self.carry_capacity - getattr(self.resources, resource_tile.acronym.lower(), 0)
        )
        setattr(self.resources, resource_tile.acronym.lower(), getattr(self.resources, resource_tile.acronym.lower(), 0) + collected)
        resource_tile.storage = Resources(
            food=resource_tile.storage.food - (collected if resource_tile.acronym == "F" else 0),
            gold=resource_tile.storage.gold - (collected if resource_tile.acronym == "G" else 0),
            wood=resource_tile.storage.wood - (collected if resource_tile.acronym == "W" else 0),
        )
        if resource_tile.storage.food <= 0 and resource_tile.storage.gold <= 0 and resource_tile.storage.wood <= 0:
            game_map.remove_entity(resource_tile, resource_tile.x, resource_tile.y)
        self.task = False

    def stockResources(self, building, game_map, team):
        if not self.isAvailable() or not hasattr(building, 'resourceDropPoint') or not building.resourceDropPoint:
            return
        self.task = 'stock'
        self.move(building.x, building.y, game_map)
        team.resources = Resources(
            food=team.resources.food + self.resources.food,
            gold=team.resources.gold + self.resources.gold,
            wood=team.resources.wood + self.resources.wood,
        )
        self.resources = Resources(food=0, gold=0, wood=0)
        self.task = False

    def build(self, map,building):
        if not self.isAvailable():
            return
        self.task = 'build'
        self.move((building.x, building.y), map)
        building.constructors.append(self)

    
    def buildTime(self, building, num_villagers):
        return max(10, (3 * building.buildTime) / (num_villagers + 2)) if num_villagers > 0 else building.buildTime
    '''