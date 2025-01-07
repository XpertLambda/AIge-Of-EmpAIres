# Models/Team.py
from Settings.setup import LEAN_STARTING_GOLD, LEAN_STARTING_FOOD, LEAN_STARTING_WOOD, LEAN_STARTING_VILLAGERS, LEAN_NUMBER_OF_TOWER_CENTRE, MEAN_STARTING_GOLD, MEAN_STARTING_FOOD, MEAN_STARTING_WOOD, MEAN_STARTING_VILLAGERS, MEAN_NUMBER_OF_TOWER_CENTRE, MARINES_STARTING_GOLD, MARINES_STARTING_FOOD, MARINES_STARTING_WOOD, MARINES_NUMBER_OF_BARRACKS, MARINES_NUMBER_OF_STABLES, MARINES_NUMBER_OF_ARCHERY_RANGES, MARINES_STARTING_VILLAGERS, START_MAXIMUM_POPULATION
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
        self.maximum_population = START_MAXIMUM_POPULATION
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
            if u.hp<=0:
                self.units.remove(u)
                
        for b in self.buildings:
            if b.hp<=0:
                self.buildings.remove(b)
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
                    print("ok")
                    l.append(entity)
                    for villager in entity.constructors:
                        villager.task=False
                    if isinstance(entity,House) or isinstance(entity,TownCentre):
                        self.maximum_population+=5
            else:
                if entity.training_time+time-clock<=0:
                    l.append(entity)
                    self.units.append(entity)
        for entity in l:
            del self.en_cours[entity]


    def buildBuilding(self,building,clock,nb,map):
        #building:batiment qu'on veut construire
        #clock: temps actuel
        #nb: nombre de villageois maximum qui va construire
       
        
        if all([unit.task for unit in self.units if isinstance(unit,Villager)]):
            print("les villageois sont occupés")
            return False
        if self.resources["wood"] >= building.cost[2]:
            self.resources["wood"] -= building.cost[2]

           
        else:
            print(f"{self}: Not enough resources.")
            return False
       #rajouter le placement sur la map ne marche pas
        if not map.place_building(building,self):
            print("cannot place")
            return False
       
        i=0
        num_constructors=0
        while(i<len(self.units) and num_constructors<nb):
            v=self.units[i]
            if isinstance(v,Villager) and not(v.task):
                v.build(map,building)
                num_constructors +=1
                v1=v
            i+=1
         
        self.en_cours[building]=clock+v1.buildTime(building,num_constructors) 


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
                soldier.attack(t,map)
            i+=1

    def modify_target(self,target,players_target):
        #arrete toutes les attaques de la team
        for unit in self.units:
            if not isinstance(unit,Villager):
                unit.target=None
        players_target[self.teamID]=target