# Models/Team.py

from Settings.setup import *
from Entity.Building import *
from Entity.Unit import *
from Entity.Resource import Resource

class Team:
    def __init__(self, difficulty, teamID, maximum_population = START_MAXIMUM_POPULATION):
        self.resources = {"gold": 0, "wood": 0, "food": 0}
        self.units = []     
        self.buildings = []
        self.teamID = teamID
        self.maximum_population = START_MAXIMUM_POPULATION
        self.army = set()
        print(f"Initialized Team {teamID} with maximum_population: {self.maximum_population}")

        
        if difficulty == 'DEBUG':
            self.resources["gold"] = LEAN_STARTING_GOLD
            self.resources["food"] = LEAN_STARTING_FOOD
            self.resources["wood"] = LEAN_STARTING_WOOD
        
            for _ in range(10):
                self.units.append(Swordsman(team = teamID))           
                self.units.append(Villager(team = teamID))           
                self.units.append(Archer(team = teamID))           
            for _ in range(5):
                self.buildings.append(TownCentre(team = teamID))
                self.buildings.append(ArcheryRange(team = teamID))
                self.buildings.append(Stable(team = teamID))
                self.buildings.append(Barracks(team = teamID))
                self.buildings.append(Keep(team = teamID))
                self.buildings.append(Camp(team = teamID))
                self.buildings.append(House(team = teamID))

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
                self.army = set()

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

    
    def gestion(self):
        for u in self.army:
            if u.hp==0:
                self.army.remove(u)
        for b in self.buildings:
            if b.hp==0:
                self.army.remove(b)


    def battle(self,t,map,nb):
        for i in range(0,len(t.army)):
            s=t.army[i]
            print("ok")
            if not(s.task):
                print("ok")
                s.task=True
                s.attaquer(False,self,map)
  
        for i in range(0,min(nb,len(self.army))):
            s=self.army[i]
            s.task=True
            s.attaquer(True,t,map)
            
    def buildBatiment(self, building, x, y, map, num_villagers):
        if not self.isAvailable():
            return
        self.task = True
        self.SeDeplacer(x, y, map)
        if not map.can_place_building(map.grid, x, y, building):
            print(f"{self.acronym}: Cannot place building.")
            self.task = False
            return
        if self.resources >= building.woodCost:
            self.resources -= building.woodCost
            print(f"{self.acronym}: Building...")
            map.place_building(x, y, building)
        else:
            print(f"{self.acronym}: Not enough resources.")
            
            # Increment max population if town centre is built
        if isinstance(building, TownCentre) or isinstance(building, House):
            self.maximum_population += building.population
            
        self.task = False
        
    