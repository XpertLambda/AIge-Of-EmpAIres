from Entity.Entity import Entity
from Settings.setup import HALF_TILE_SIZE
from Controller.isometric_utils import tile_to_screen
from Controller.init_assets import draw_sprite

class Resource(Entity):
    def __init__(self, x, y, acronym, storage, max_hp, variant=0):
        super().__init__(x=x, y=y,  team=None, size = 1, max_hp=max_hp, acronym=acronym)
        
        self.storage = storage
        self.variant = variant
        
    def __str__(self):
        return f"Gold: {self.gold}, Wood: {self.wood}, Food: {self.food}"

    def update(self, game_map, dt):
        if not self.isAlive():
            self.kill()

    def kill(self):
        self.current_frame = 0
        self.hp = 0
        self.state = 7

    def display(self, screen, screen_width, screen_height, camera, dt):
        category = 'resources'
        screen_x, screen_y = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, category, screen_x, screen_y, camera.zoom, variant=self.variant)