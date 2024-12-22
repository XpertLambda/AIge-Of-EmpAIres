from Entity.Entity import Entity
from Settings.setup import HALF_TILE_SIZE
from Controller.isometric_utils import tile_to_screen
from Controller.init_sprites import draw_sprite

class Resource(Entity):
    def __init__(self, x, y, acronym, storage, max_hp, variant=0):
        super().__init__(x=x, y=y,  team=None, size = 1, max_hp=max_hp, acronym=acronym)
        
        self.storage = storage
        self.variant = variant

    def display(self, screen, screen_width, screen_height, camera):
        category = 'resources'
        screen_x, screen_y = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, category, screen_x, screen_y, camera.zoom, variant=self.variant)