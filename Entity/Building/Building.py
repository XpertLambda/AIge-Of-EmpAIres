from Entity.Entity import *
from Controller.isometric_utils import *
from Settings.setup import *
from Controller.init_sprites import draw_sprite

class Building(Entity):
    def __init__(self, x, y, team, acronym, woodCost, goldCost, buildTime, hp, size, population=0, resourceDropPoint=False, spawnsUnits=False, containsFood=False, walkable=False, attack=0, range=0):
        super().__init__(x, y, team, acronym, size)
        self.woodCost = woodCost
        self.goldCost = goldCost
        self.buildTime = buildTime
        self.hp = hp
        self.max_hp = self.hp  # ajout de la définition de max_hp
        self.population = population
        self.resourceDropPoint = resourceDropPoint
        self.spawnsUnits = spawnsUnits
        self.containsFood = containsFood
        self.walkable = walkable
        self.attack = attack
        self.range = range

    def display(self, screen, screen_width, screen_height, camera):
        category = 'buildings'
        screen_x, screen_y = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, category, screen_x, screen_y, camera.zoom, team=self.team)

    def is_walkable(self):
        return self.walkable
