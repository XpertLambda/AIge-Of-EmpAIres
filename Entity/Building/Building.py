from Entity.Entity import Entity
from Controller.utils import tile_to_screen
from Settings.setup import HALF_TILE_SIZE, FRAMES_PER_BUILDING, GAME_SPEED
from Settings.setup import HALF_TILE_SIZE, GAME_SPEED
from Controller.drawing import draw_sprite
from random import randint
from AiUtils.aStar import a_star
from Entity.Unit.Archer import Archer
from Entity.Unit.Swordsman import Swordsman
from Entity.Unit.Horseman import Horseman
from Entity.Unit.Villager import Villager
from Models.Resources import Resources

UNIT_TRAINING_MAP = {
    'T': 'villager',   # TownCentre => Villager
    'A': 'archer',     # ArcheryRange => Archer
    'B': 'swordsman',  # Barracks => Swordsman
    'S': 'horseman'    # Stable => Horseman
}
UNIT_CLASSES = {
    'villager':  Villager,
    'archer':    Archer,
    'swordsman': Swordsman,
    'horseman':  Horseman,
}

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
        population = 0, 
        resourceDropPoint = False,
        spawnsUnits = False, 
        walkable = False,
        attack_power = 0, 
        attack_range = 0,
        hasResources = False,
    ):
        super().__init__(
            x=x, 
            y=y, 
            team=team, 
            acronym=acronym, 
            size=size, 
            max_hp=max_hp, 
            cost=cost, 
            walkable=walkable,
            hasResources=hasResources
        )
        self.buildTime = buildTime
        self.builders = None

        self.population = population
        self.resourceDropPoint = resourceDropPoint
        self.spawnsUnits = spawnsUnits
        self.attack_power = attack_power
        self.attack_range = attack_range
        self.constructors = []

        self.frames = FRAMES_PER_BUILDING

        self.training_queue = []
        self.current_training_unit = None
        self.current_training_time_left = 0
        self.training_progress = 0.0
        self.removed = False

    # ---------------- Update Entity --------------
    def update(self, game_map, dt):
        if self.isAlive():
            self.seekConstruction(dt)              
            if self.spawnsUnits:
                self.update_training(dt, game_map, self.team)

        else:
            self.death(game_map)
        self.animator(dt)

    # ---------------- Controller ----------------
    def kill(self):
        self.state = 'death'
        self.current_frame = 0
        self.hp = 0

    def death(self, game_map):
        if self.state != 'death' :
            self.kill()

        if self.current_frame == self.frames - 1 and self.state == 'death':
            self.state = ''

        if self.state == 7 and not self.removed:
            self.removed = True
            for player in game_map.game_state['players']:
                if hasattr(player, 'buildings') and self in player.buildings:
                    player.buildings.remove(self)
                    break
            game_map.remove_entity(self)
            game_map.game_state['player_info_updated'] = True

    def is_walkable(self):
        return self.walkable
    
    # ---------------- Display Logic ----------------
    def animator(self, dt):
        if self.state != '':
            self.frame_duration += dt
            frame_time = 1.0 / self.frames
            if self.frame_duration >= frame_time:
                self.frame_duration -= frame_time
                self.current_frame = (self.current_frame + 1) % self.frames

        if self.cooldown_frame:
            self.current_frame = self.cooldown_frame

    def display(self, screen, screen_width, screen_height, camera, dt):
        if self.state == 'death' or self.state == 'idle':
            sx, sy = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)
            draw_sprite(screen, self.acronym, 'buildings', sx, sy, camera.zoom, state=self.state, frame=self.current_frame)

    # ---------------- Display Logic ----------------

    def add_to_training_queue(self, team):
        """
        Attempt to enqueue a new unit if enough resources. 
        Return True if successful, False otherwise.
        """
        if self.acronym not in UNIT_TRAINING_MAP:
            return False

        unit_name = UNIT_TRAINING_MAP[self.acronym]
        unit_class = UNIT_CLASSES[unit_name]
        unit = unit_class(team=self.team)


        if (team.resources.has_enough(unit.cost.get()) and team.population < team.maximum_population ):
            team.resources.decrease_resources(unit.cost.get())
            self.training_queue.append(unit_name)
            return True

        return False

    # ---------------- Train Logic ----------------

    def update_training(self, delta_time, game_map, team):
        """
        Updates the building's training queue each frame.
        """
        if not self.training_queue and not self.current_training_unit:
            return

        if not self.current_training_unit:
            next_unit_name = self.training_queue.pop(0)
            unit_class = UNIT_CLASSES[next_unit_name]
            unit = unit_class(team=self.team)
            self.current_training_unit = next_unit_name
            self.current_training_time_left = unit.training_time / GAME_SPEED
            self.training_progress = 0.0

        if self.current_training_unit:
            self.current_training_time_left -= delta_time
            unit_class = UNIT_CLASSES[self.current_training_unit]
            total_time = unit_class(team=self.team).training_time / GAME_SPEED
            self.training_progress = max(0.0, min(1.0, 1.0 - (self.current_training_time_left / total_time)))

            if self.current_training_time_left <= 0:
                self.spawn_trained_unit(self.current_training_unit, game_map, team)
                self.current_training_unit = None
                self.current_training_time_left = 0
                self.training_progress = 0.0

    def spawn_trained_unit(self, unit_name, game_map, team):
        """
        Once the unit is fully trained, find a free adjacent tile, place the unit, 
        and make it move randomly away from the building.
        """
        unit_class = UNIT_CLASSES[unit_name]
        spawn_tile = self.find_adjacent_tile(game_map)
        if not spawn_tile:
            return

        new_unit = unit_class(team=self.team)
        placed_ok = game_map.add_entity(new_unit, spawn_tile[0], spawn_tile[1])
        if not placed_ok:
            return

        game_map.game_state['player_info_updated'] = True
        self.move_unit_randomly(new_unit, game_map)

    def find_adjacent_tile(self, game_map):
        """
        Search tiles around the building in an expanding square to find a walkable one.
        """
        base_x, base_y = round(self.x), round(self.y)
        for radius in range(1, 8):
            for check_x in range(base_x - radius, base_x + radius + 1):
                for check_y in range(base_y - radius, base_y + radius + 1):
                    if (0 <= check_x < game_map.num_tiles_x and 
                        0 <= check_y < game_map.num_tiles_y):
                        if game_map.walkable_position((check_x, check_y)):
                            return (check_x, check_y)
        return None

    def move_unit_randomly(self, new_unit, game_map):
        """
        Move newly spawned unit up to ~5 tiles away randomly, if walkable.
        Makes up to 10 attempts to find a walkable position.
        If no walkable position is found, unit stays near the building.
        """
        origin_x, origin_y = round(new_unit.x), round(new_unit.y)
        max_attempts = 10
        
        for attempt in range(max_attempts):
            offset_x = randint(-5, 5)
            offset_y = randint(-5, 5)
            target_x = origin_x + offset_x
            target_y = origin_y + offset_y
            
            if (0 <= target_x < game_map.num_tiles_x and 
                0 <= target_y < game_map.num_tiles_y and
                game_map.walkable_position((target_x, target_y))):
                # Calculer ET assigner le path à l'unité
                new_unit.set_destination((target_x, target_y), game_map)
                new_unit.destination = (target_x, target_y)
                return

    # ---------------- Stock Logic ----------------
    
    def stock(self, game_map, resources):
        if self.resourceDropPoint:
            team_resources = game_map.players[self.team].resources
            if team_resources.increase_resources(resources):
                return resources
        return None

    # ---------------- Build Logic ----------------
    def construct(self, builders):
        self.builders = builders
        self.buildTime = self.get_buildTime(len(builders))

    def get_buildTime(self, num_villagers):
        return (3 * self.buildTime) / (num_villagers + 2) if num_villagers > 0 else self.buildTime

    def seekConstruction(self, dt):
        if self.buildTime <= 0 or not self.builders:
            return
        print("construction")
        self.state = 'construction'
        for builder in self.builders.copy():
            if not builder.isAlive() or builder.state != 'build' or builder.state != 'repair':
                self.builders.remove(builder)

        if self.hp < self.max_hp:
            for builder in self.builders:
                if builder.task != 'repair':  
                    builder.set_task('repair', builder)
            return        
        self.buildTime -= dt
