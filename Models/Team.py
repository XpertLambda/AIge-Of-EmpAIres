# Chemin de /home/cyril/Documents/INSA/Projet_python/Models/Team.py
from Settings.setup import (
    LEAN_STARTING_GOLD, LEAN_STARTING_FOOD, LEAN_STARTING_WOOD,
    LEAN_STARTING_VILLAGERS, LEAN_NUMBER_OF_TOWER_CENTRE, MEAN_STARTING_GOLD,
    MEAN_STARTING_FOOD, MEAN_STARTING_WOOD, MEAN_STARTING_VILLAGERS,
    MEAN_NUMBER_OF_TOWER_CENTRE, MARINES_STARTING_GOLD, MARINES_STARTING_FOOD,
    MARINES_STARTING_WOOD, MARINES_NUMBER_OF_BARRACKS, MARINES_NUMBER_OF_STABLES,
    MARINES_NUMBER_OF_ARCHERY_RANGES, MARINES_STARTING_VILLAGERS,
    START_MAXIMUM_POPULATION,
    Resources
)
from Entity.Building import *
from Entity.Unit import *
from Entity.Resource import Resource
from Models.Map import GameMap

def get_building_tiles(building, game_map):
    """
    Return all (x,y) tiles that 'building' occupies in game_map.grid.
    """
    results = []
    x_min = max(0, round(building.x) - building.size)
    x_max = min(game_map.num_tiles_x, round(building.x) + building.size)
    y_min = max(0, round(building.y) - building.size)
    y_max = min(game_map.num_tiles_y, round(building.y) + building.size)
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            tile_pos = (x, y)
            ent_set = game_map.grid.get(tile_pos, None)
            if ent_set and building in ent_set:
                results.append((x, y))
    return results

class Team:
    def __init__(self, difficulty, teamID, maximum_population=START_MAXIMUM_POPULATION):
        self.resources = {"gold": 0, "wood": 0, "food": 0}
        self.units = []
        self.buildings = []
        self.teamID = teamID
        self.maximum_population = maximum_population
        self.en_cours = dict()

        if difficulty == 'DEBUG':
            self.resources["gold"] = LEAN_STARTING_GOLD
            self.resources["food"] = LEAN_STARTING_FOOD
            self.resources["wood"] = LEAN_STARTING_WOOD

            for _ in range(20):
                self.units.append(Horseman(team=teamID))
                self.units.append(Villager(team=teamID))
                self.units.append(Archer(team=teamID))
                self.units.append(Swordsman(team=teamID))

            for _ in range(20):
                self.buildings.append(TownCentre(team=teamID))
                self.buildings.append(ArcheryRange(team=teamID))
                self.buildings.append(Stable(team=teamID))
                self.buildings.append(Barracks(team=teamID))
                self.buildings.append(Keep(team=teamID))
                self.buildings.append(Camp(team=teamID))
                self.buildings.append(House(team=teamID))
                self.buildings.append(Farm(team=teamID))

        elif difficulty == 'lean':
            self.resources["gold"] = LEAN_STARTING_GOLD
            self.resources["food"] = LEAN_STARTING_FOOD
            self.resources["wood"] = LEAN_STARTING_WOOD

            for _ in range(LEAN_STARTING_VILLAGERS):
                self.units.append(Villager(team=teamID))
            for _ in range(LEAN_NUMBER_OF_TOWER_CENTRE):
                self.buildings.append(TownCentre(team=teamID))

        elif difficulty == 'mean':
            self.resources["gold"] = MEAN_STARTING_GOLD
            self.resources["food"] = MEAN_STARTING_FOOD
            self.resources["wood"] = MEAN_STARTING_WOOD
            for _ in range(MEAN_STARTING_VILLAGERS):
                self.units.append(Villager(team=teamID))
            for _ in range(MEAN_NUMBER_OF_TOWER_CENTRE):
                self.buildings.append(TownCentre(team=teamID))
                self.units = set()

        elif difficulty == 'marines':
            self.resources["gold"] = MARINES_STARTING_GOLD
            self.resources["food"] = MARINES_STARTING_FOOD
            self.resources["wood"] = MARINES_STARTING_WOOD
            # Ajout des bâtiments
            for _ in range(MARINES_NUMBER_OF_BARRACKS):
                self.buildings.append(Barracks(team=teamID))
            for _ in range(MARINES_NUMBER_OF_STABLES):
                self.buildings.append(Stable(team=teamID))
            for _ in range(MARINES_NUMBER_OF_ARCHERY_RANGES):
                self.buildings.append(ArcheryRange(team=teamID))
            for _ in range(MARINES_STARTING_VILLAGERS):
                self.units.append(Villager(team=teamID))

    def manage_life(self, game_map):
        """
        Removes dead units and buildings from both team-lists 
        and from game_map.grid. 
        Ensures building vanish from the map if hp <=0.
        """
        # Remove dead units
        for u in self.units[:]:
            if u.hp <= 0:
                game_map.remove_entity(u, round(u.x), round(u.y))
                self.units.remove(u)

        # Remove dead buildings
        for b in self.buildings[:]:
            if b.hp <= 0:
                # remove from all relevant tiles
                tiles = get_building_tiles(b, game_map)
                for (tx, ty) in tiles:
                    ent_set = game_map.grid.get((tx, ty), None)
                    if ent_set and b in ent_set:
                        ent_set.remove(b)
                    if ent_set and len(ent_set) == 0:
                        del game_map.grid[(tx, ty)]
                self.buildings.remove(b)

        # Non-Villager => .task=False
        for s in self.units:
            if not isinstance(s, Villager):
                s.task = False

    def manage_creation(self, clock):
        """
        Manages creation of buildings/units in self.en_cours.
        Once time is up => place them in .units or .buildings.
        """
        to_remove = []
        for entity, start_time in self.en_cours.items():
            if isinstance(entity, Building):
                if start_time - clock <= 0:
                    self.buildings.append(entity)
                    to_remove.append(entity)
                    for villager in entity.constructors:
                        villager.task = False
            else:
                if entity.training_time + start_time - clock <= 0:
                    to_remove.append(entity)
                    self.units.append(entity)

        for entity in to_remove:
            del self.en_cours[entity]

    def buildBatiment(self, building, clock, nb, game_map):
        """
        Up to nb villagers build a new building => cost wood => en_cours building
        """
        if all([v.task for v in self.units if isinstance(v, Villager)]):
            print("All villagers are busy.")
            return False

        if self.resources["wood"] >= building.cost.wood:
            self.resources["wood"] -= building.cost.wood
        else:
            print(f"Team {self.teamID}: Not enough wood.")
            return False

        i = 0
        j = 0
        chosen_villager = None
        while i < len(self.units) and j < nb:
            v = self.units[i]
            if isinstance(v, Villager) and not v.task:
                v.build(game_map, building)
                j += 1
                chosen_villager = v
            i += 1

        if chosen_villager:
            total_build_time = chosen_villager.buildTime(building, j)
            self.en_cours[building] = clock + total_build_time
        else:
            print("No free villager found to build.")
            return False
        return True

    def battle(self,t,map,nb):
        for i in range(0,len(t.units)):
            s=t.units[i]
            if not(s.task) and not(isinstance(s,Villager)):
                print("ok")
                s.task=True
                s.attaquer(False,self,map)
  
        for i in range(0,min(nb,len(self.units))):
            s=self.units[i]
            if not(isinstance(s,Villager)):
               
                s.task=True
                s.attaquer(True,t,map)

    def collectResource(self, villager, resource_tile, duration, game_map):
        if not isinstance(villager, Villager):
            return
        if not villager.isAvailable():
            return
        villager.task = True
        villager.move(resource_tile.x, resource_tile.y, game_map)
        collected = min(
            villager.resource_rate * duration,
            villager.carry_capacity - getattr(villager.resources, resource_tile.acronym.lower(), 0)
        )
        setattr(villager.resources, resource_tile.acronym.lower(), getattr(villager.resources, resource_tile.acronym.lower(), 0) + collected)
        resource_tile.storage = Resources(
            food=resource_tile.storage.food - (collected if resource_tile.acronym == "F" else 0),
            gold=resource_tile.storage.gold - (collected if resource_tile.acronym == "G" else 0),
            wood=resource_tile.storage.wood - (collected if resource_tile.acronym == "W" else 0),
        )
        if resource_tile.storage.food <= 0 and resource_tile.storage.gold <= 0 and resource_tile.storage.wood <= 0:
            game_map.remove_entity(resource_tile, resource_tile.x, resource_tile.y)
        villager.task = False

    def stockResources(self, villager, building, game_map):
        if not isinstance(villager, Villager):
            return
        if not villager.isAvailable() or not hasattr(building, 'resourceDropPoint') or not building.resourceDropPoint:
            return
        villager.task = True
        villager.move(building.x, building.y, game_map)
        self.resources = Resources(
            food=self.resources["food"] + villager.resources.food,
            gold=self.resources["gold"] + villager.resources.gold,
            wood=self.resources["wood"] + villager.resources.wood,
        )
        villager.resources = Resources(food=0, gold=0, wood=0)
        villager.task = False
