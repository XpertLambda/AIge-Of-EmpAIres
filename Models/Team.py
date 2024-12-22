# Models/Team.py
from Settings.setup import LEAN_STARTING_GOLD, LEAN_STARTING_FOOD, LEAN_STARTING_WOOD, LEAN_STARTING_VILLAGERS, LEAN_NUMBER_OF_TOWER_CENTRE, MEAN_STARTING_GOLD, MEAN_STARTING_FOOD, MEAN_STARTING_WOOD, MEAN_STARTING_VILLAGERS, MEAN_NUMBER_OF_TOWER_CENTRE, MARINES_STARTING_GOLD, MARINES_STARTING_FOOD, MARINES_STARTING_WOOD, MARINES_NUMBER_OF_BARRACKS, MARINES_NUMBER_OF_STABLES, MARINES_NUMBER_OF_ARCHERY_RANGES, MARINES_STARTING_VILLAGERS
from Entity.Building import *
from Entity.Unit import *
from Entity.Resource import Resource

class Team:
    def __init__(self, difficulty, teamID):
        self.resources = {"gold": 0, "wood": 0, "food": 0}
        self.units = []     
        self.buildings = []
        self.teamID = teamID
        self.en_cours=dict()
        if difficulty == 'DEBUG':
            self.resources["gold"] = LEAN_STARTING_GOLD
            self.resources["food"] = LEAN_STARTING_FOOD
            self.resources["wood"] = LEAN_STARTING_WOOD
        
            for _ in range(10):
                self.units.append(Swordsman(team = teamID))           
                self.units.append(Villager(team = teamID))           
                self.units.append(Horseman(team = teamID))           
            for _ in range(5):
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

##### A MODIFIER!!!!!!!!
'''
    def gestion(self):
        for unit in self.units:
            if unit.hp==0:
                self.units.remove(unit)
        for b in self.buildings:
            if b.hp==0:
                self.units.remove(b)
        for i in range(0,len(self.units)):
            s=self.units[i]
            if not(isinstance(s,Villager)):
                
                s.task=False

    def gestion_crea(self,clock):
        for e,t in self.en_cours.items:
            
            if isinstance(e,Building):
                if clock-t==e.build_time:
                    self.buildings.append(e)
            else:
                if clock-t==e.training_time:
                    self.units.append(e)

        for i in range(0,len(self.units)):
                if not(isinstance(s,Villager)):
                    s=self.units[i]
                    s.task=False

    def bat(self, building,clock,nb):
        if not map.can_place_building(map.grid, x, y, building):
            print(f"{self.acronym}: Cannot place building.")
            return False
        if all([e.task for e in self.units if isinstance(e,Villager)]):
            print("les villageois sont occupés")
            return False
        if self.resources >= building.woodCost:
            self.resources -= building.woodCost
            print(f"{self.acronym}: Building...")

            map.place_building(x, y, building)
        else:
            print(f"{self.acronym}: Not enough resources.")
            return False
        i=0
        while(i<len(self.units and i<nb)):
            v=self.units[i]
            if isinstance(v,Villager) and not(v.task):
                #v.buildBatiment() a finir
                pass

        building.build_time=v.buildTime(buldingi)
        t.en_cours[building]=clock


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

    def defense_villageois(self):
       #sert a faire defendre tout le monde meme les villageois
       #doit etre utiliser avant battle
         for i in range(0,len(self.units)):
                s=self.units[i]
                s.task=True   
                s.attaquer(False,self.cible,map)
'''