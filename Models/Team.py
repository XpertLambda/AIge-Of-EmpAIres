# Models/Team.py
from Settings.setup import LEAN_STARTING_GOLD, LEAN_STARTING_FOOD, LEAN_STARTING_WOOD, LEAN_STARTING_VILLAGERS, LEAN_NUMBER_OF_TOWER_CENTRE, MEAN_STARTING_GOLD, MEAN_STARTING_FOOD, MEAN_STARTING_WOOD, MEAN_STARTING_VILLAGERS, MEAN_NUMBER_OF_TOWER_CENTRE, MARINES_STARTING_GOLD, MARINES_STARTING_FOOD, MARINES_STARTING_WOOD, MARINES_NUMBER_OF_BARRACKS, MARINES_NUMBER_OF_STABLES, MARINES_NUMBER_OF_ARCHERY_RANGES, MARINES_STARTING_VILLAGERS, START_MAXIMUM_POPULATION, Resources
from Entity.Building import *
from Entity.Unit import *
from Entity.Resource import Resource
from Models.Map import GameMap


class Team:
    def __init__(self, difficulty, teamID, maximum_population = START_MAXIMUM_POPULATION):
        self.resources = {"gold": 0, "wood": 0, "food": 0}
        self.units = []     
        self.buildings = []
        self.teamID = teamID
        self.maximum_population = maximum_population
        self.en_cours=dict()
        if difficulty == 'DEBUG':
            self.resources["gold"] = LEAN_STARTING_GOLD
            self.resources["food"] = LEAN_STARTING_FOOD
            self.resources["wood"] = LEAN_STARTING_WOOD
        
            for _ in range(30):
                self.units.append(Horseman(team = teamID))
                self.units.append(Villager(team = teamID))
                self.units.append(Archer(team = teamID))
                self.units.append(Swordsman(team = teamID))
            for _ in range(10):
                self.buildings.append(TownCentre(team = teamID))
                self.buildings.append(ArcheryRange(team = teamID))
                self.buildings.append(Stable(team = teamID))
                self.buildings.append(Barracks(team = teamID))
                self.buildings.append(Keep(team = teamID))
                self.buildings.append(Camp(team = teamID))
                self.buildings.append(House(team = teamID))
                self.buildings.append(Farm(team = teamID))

        elif difficulty == 'lean':
            self.resources["gold"] = LEAN_STARTING_GOLD
            self.resources["food"] = LEAN_STARTING_FOOD
            self.resources["wood"] = LEAN_STARTING_WOOD  

            for _ in range(LEAN_STARTING_VILLAGERS):
                self.units.append(Villager(team = teamID))           
            for _ in range(LEAN_NUMBER_OF_TOWER_CENTRE):
                self.buildings.append(TownCentre(team = teamID))  

        elif difficulty == 'mean':
            self.resources["gold"] = MEAN_STARTING_GOLD
            self.resources["food"] = MEAN_STARTING_FOOD
            self.resources["wood"] = MEAN_STARTING_WOOD
            for _ in range(MEAN_STARTING_VILLAGERS):
                self.units.append(Villager(team = teamID))
            for _ in range(MEAN_NUMBER_OF_TOWER_CENTRE):
                self.buildings.append(TownCentre(team = teamID))
                self.units = set()

        elif difficulty == 'marines':
            self.resources["gold"] = MARINES_STARTING_GOLD
            self.resources["food"] = MARINES_STARTING_FOOD
            self.resources["wood"] = MARINES_STARTING_WOOD
            # Ajout des bâtiments
            for _ in range(MARINES_NUMBER_OF_BARRACKS):
                self.buildings.append(Barracks(team = teamID))

            for _ in range(MARINES_NUMBER_OF_STABLES):
                self.buildings.append(Stable(team = teamID))

            for _ in range(MARINES_NUMBER_OF_ARCHERY_RANGES):
                self.buildings.append(ArcheryRange(team = teamID))
            for _ in range(MARINES_STARTING_VILLAGERS):
                self.units.append(Villager(team = teamID))

    def manage_life(self):
        for u in self.units:
            if u.hp==0:
                self.units.remove(u)
        for b in self.buildings:
            if b.hp==0:
                self.units.remove(b)
        for i in range(0,len(self.units)):
            s=self.units[i]
            if not(isinstance(s,Villager)):
                
                s.task=False

    def manage_creation(self,clock):
        l=[]
        for entity,time in self.en_cours.items():
            
            if isinstance(entity,Building):
                if time-clock<=0:
                    self.buildings.append(entity)
                    l.append(entity)
                    for villager in entity.constructors:
                        villager.task=False
            else:
                if entity.training_time+time-clock<=0:
                    l.append(entity)
                    self.units.append(entity)
        for entity in l:
            del self.en_cours[entity]


    def buildBatiment(self,building,clock,nb,map):
        #building:batiment qu'on veut construire
        #clock: temps actuel
        #nb: nombre de villageois maximum qui va construire
       
        
        if all([e.task for e in self.units if isinstance(e,Villager)]):
            print("les villageois sont occupés")
            return False
        if self.resources["wood"] >= building.cost[2]:
            self.resources["wood"] -= building.cost[2]

           
        else:
            print(f"{self}: Not enough resources.")
            return False
       #rajouter le placement sur la map ne marche pas
        """
        if not map.place_building(building,self):
            print("cannot place")
            return False
        """
        i=0
        j=0
        while(i<len(self.units) and j<nb):
            v=self.units[i]
            if isinstance(v,Villager) and not(v.task):
                v.build(map,building)
                j+=1
                v1=v
            i+=1
         
        self.en_cours[building]=clock+v1.buildTime(building,j) 


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