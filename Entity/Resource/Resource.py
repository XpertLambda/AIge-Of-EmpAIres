from Entity.Entity import Entity
from Settings.setup import HALF_TILE_SIZE
from Controller.utils import tile_to_screen
from Controller.drawing import draw_sprite
from copy import copy

class Resource(Entity):
    def __init__(self, x, y, acronym, storage, max_hp, variant=0):
        super().__init__(x = x, y = y,  team = None,  acronym = acronym, size = 1, max_hp = max_hp, hasResources = True)
        
        self.storage = storage.copy()
        self.maximum_storage = storage.copy()
        self.variant = variant

    def update(self, game_map, dt):
        self.animator(dt)
        if not self.isAlive():
            self.kill()

    def kill(self):
        self.current_frame = 0
        self.hp = 0
        self.state = ''

    def animator(self, dt):
        self.variant = self.get_variant()

    def display(self, screen, screen_width, screen_height, camera, dt):
        screen_x, screen_y = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, 'resources', screen_x, screen_y, camera.zoom, variant=self.variant)