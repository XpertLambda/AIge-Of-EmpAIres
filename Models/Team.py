from Settings.setup import *
from collections import Counter
from Entity.Entity import *
from Entity.Building import *
from Entity.Unit import *
from Entity.Resource import Resource
from Models.Map import GameMap

class Team:
    def __init__(self, difficulty, teamID):
        self.resources = {"gold": 0, "wood": 0, "food": 0}
        self.units = []
        self.buildings = []
        self.teamID = teamID
        self.maximum_population = MAXIMUM_POPULATION
        self.en_cours = dict()

        if difficulty == 'DEBUG':
            self.resources["gold"] = LEAN_STARTING_GOLD
            self.resources["food"] = LEAN_STARTING_FOOD
            self.resources["wood"] = LEAN_STARTING_WOOD

            for _ in range(30):
                self.units.append(Horseman(team=teamID))
                self.units.append(Villager(team=teamID))
                self.units.append(Archer(team=teamID))
                self.units.append(Swordsman(team=teamID))

            for _ in range(5):
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
            for _ in range(MARINES_NUMBER_OF_TOWER_CENTRE):
                self.buildings.append(TownCentre(team=teamID))
                
    
    def manage_life(self):
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
                    for villager in entity.constructors:
                        villager.task=False
                    if isinstance(entity,House) or isinstance(entity,TownCentre):
                        self.maximum_population+=5
                    to_remove.append(entity)
                    for villager in entity.constructors:
                        villager.task = False
            else:
                if entity.training_time + start_time - clock <= 0:
                    to_remove.append(entity)
                    self.units.append(entity)

        for entity in to_remove:
            del self.en_cours[entity]

    def buildBuilding(self, building, clock, nb, game_map):
        if all([v.task for v in self.units if isinstance(v, Villager)]):
            print("All villagers are busy.")
            return False

        if self.resources["wood"] >= building.cost.wood:
            self.resources["wood"] -= building.cost.wood
        else:
            print(f"Team {self.teamID}: Not enough wood.")
            return False
        if not game_map.place_building(building,self):
            print("cannot place")
            return False
       
        i=0
        num_constructors=0
        while(i<len(self.units) and num_constructors<nb):
            unit=self.units[i]
            if isinstance(unit,Villager) and not(unit.task):
                unit.build(map,building)
                num_constructors +=1
                v1=v
            i+=1
         
        self.en_cours[building]=clock+v1.buildTime(building,num_constructors) 

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
        #attaque et l'adversaire défend
        for i in range(0,len(t.units)):
            soldier=t.units[i]
            if not(soldier.task) and not(isinstance(soldier,Villager)):
                print("ok")
                soldier.task=True
                soldier.attack(self,map)
    
        for i in range(0,min(nb,len(self.units))):
            soldier=self.units[i]
            if not(soldier.task) and not(isinstance(soldier,Villager)):
               
                soldier.task=True
                soldier.attack(t,map)

    def battle_v2(self,t,map,nb):
        #attaque et l'adversaire ne défend pas
        i=0
        nb_soldier=0
        while(i<len(self.units) and nb_soldier< nb):
            soldier=self.units[i]
            if not(soldier.task) and not(isinstance(soldier,Villager)):
                nb_soldier+=1
                soldier.task=True
                if unit.target:
                    soldier.attack(t,map)
            i+=1

    def modify_target(self,target,players_target):
        #arrete toutes les attaques de la team
        players_target[self.teamID]=target
        for unit in self.units:
            if not isinstance(unit,Villager):
                unit.target=None
                unit.task=True
                if unit.target:
                    unit.attack(target,map)

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
