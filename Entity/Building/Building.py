from Entity.Entity import Entity
from Controller.isometric_utils import tile_to_screen
from Settings.setup import HALF_TILE_SIZE, FRAMES_PER_BUILDING
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
        attack_range=0,
    ):
        super().__init__(x=x, y=y, team=team, acronym=acronym, size=size, max_hp=max_hp, cost=cost, walkable=walkable)
        self.buildTime = buildTime
        self.population = population
        self.resourceDropPoint = resourceDropPoint
        self.spawnsUnits = spawnsUnits
        self.containsFood = containsFood
        self.walkable = walkable
        self.attack_power = attack_power
        self.attack_range = attack_range
        self.constructors=[] #liste des villageois qui construisent le batiment

        self.state = 3
        self.frames = FRAMES_PER_BUILDING
        self.current_frame = 0
        self.frame_duration = 0

    def kill(self, game_map):
        self.state = 3
        self.current_frame = 0
        self.hp = 0
        game_map.move_to_inactive(self)
        game_map.players[self.team].buildings.remove(self)

    def death(self, game_map):
        if self.current_frame == self.frames - 1:
            game_map.remove_inactive(self)

    def display(self, screen, screen_width, screen_height, camera, dt):
        if self.state !=0:
            self.frame_duration += dt
            frame_time = 1.0 / self.frames
            if self.frame_duration >= frame_time:
                self.frame_duration -= frame_time
                self.current_frame = (self.current_frame + 1) % self.frames

        sx, sy = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
        draw_sprite(screen, self.acronym, 'buildings', sx, sy, camera.zoom, state=self.state, frame=self.current_frame)


    def is_walkable(self):
        return self.walkable
