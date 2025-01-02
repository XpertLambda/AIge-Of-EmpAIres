from Entity.Entity import Entity
from Controller.isometric_utils import tile_to_screen
from Settings.setup import HALF_TILE_SIZE
from Controller.init_assets import draw_sprite

class Building(Entity):
    def __init__(
        self, 
        x, 
        y, 
        team, 
        acronym, 
        size, 
        max_hp, 
        cost, 
        buildTime, 
        population=0, 
        resourceDropPoint=False,
        spawnsUnits=False, 
        containsFood=False, 
        walkable=False,
        attack_power=0, 
        attack_range=0
    ):
        super().__init__(x=x, y=y, team=team, acronym=acronym, size=size, max_hp=max_hp, cost=cost)
        self.buildTime = buildTime
        self.population = population
        self.resourceDropPoint = resourceDropPoint
        self.spawnsUnits = spawnsUnits
        self.containsFood = containsFood
        self.walkable = walkable
        self.attack_power = attack_power
        self.attack_range = attack_range
        self.constructors=[] #liste des villageois qui construisent le batiment

    def display(self, screen, screen_width, screen_height, camera, dt):
        category = 'buildings'
        screen_x, screen_y = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, category, screen_x, screen_y, camera.zoom)

    def is_walkable(self):
        return self.walkable
