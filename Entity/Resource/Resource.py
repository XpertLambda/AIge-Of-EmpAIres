from Entity.Entity import Entity
from Settings.setup import HALF_TILE_SIZE
from Controller.utils import tile_to_screen
from Controller.init_assets import draw_sprite
from copy import copy

class Resource(Entity):
    def __init__(self, x, y, acronym, storage, max_hp, variant=0):
        super().__init__(x = x, y = y,  team = None,  acronym = acronym, size = 1, max_hp = max_hp, hasResources = True)
        
        self.storage = storage.copy()
        self.maximum_storage = storage.copy()
        self.variant = variant

    def update(self, game_map, dt):
        if not self.isAlive():
            self.kill()

    def kill(self):
        self.current_frame = 0
        self.hp = 0
        self.state = 7

    def display(self, screen, screen_width, screen_height, camera, dt):
        category = 'resources'
        variant = self.get_variant()
        screen_x, screen_y = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, category, screen_x, screen_y, camera.zoom, variant=variant)