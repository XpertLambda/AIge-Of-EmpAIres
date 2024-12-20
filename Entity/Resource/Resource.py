from Entity.Entity import Entity
from Settings.setup import *
from Controller.isometric_utils import *
from Controller.init_sprites import draw_sprite
import random 

class Resource(Entity):
    def __init__(self, x, y, acronym, capacity, team = None, variant=0):
        super().__init__(x, y, team, acronym, size = 1)
        self.capacity = capacity
        self.variant = variant

    def display(self, screen, screen_width, screen_height, camera):
        category = 'resources'
        screen_x, screen_y = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, category, screen_x, screen_y, camera.zoom, variant=self.variant)