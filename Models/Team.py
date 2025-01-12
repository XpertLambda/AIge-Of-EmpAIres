from collections import Counter
from Settings.setup import *
from Settings.entity_mapping import *
from Entity.Entity import *
from Entity.Building import *
from Entity.Unit import *
from Entity.Resource import Resource
from Models.Map import GameMap

class Team:
    def __init__(self, difficulty, teamID):
        self.resources = difficulty_config[difficulty]['Resources'].copy()

        self.units = set()
        self.buildings = set()
        self.teamID = teamID

        self.population = 0
        self.maximum_population = 0
        self.en_cours = {}

        for building, amount in difficulty_config[difficulty]['Buildings'].items():
            for _ in range(amount):
                if building in building_class_map:
                    self.add_member(building_class_map[building](team=teamID))

        for unit, amount in difficulty_config[difficulty]['Units'].items():
            for _ in range(amount):
                if unit in unit_class_map:
                    self.add_member(unit_class_map[unit](team=teamID))

    def add_member(self, entity):
        if entity.team == self.teamID :
            if entity in self.buildings or entity in self.units:
                return False

            if isinstance(entity, Building):
                if entity.population + self.maximum_population > MAXIMUM_POPULATION :
                    print("Maximum population reached")
                    return False

                self.buildings.add(entity)
                self.maximum_population += entity.population
                print(f'addded {entity} : {entity.entity_id} to team #{entity.team}')
                return True

            elif isinstance(entity, Unit):
                if self.population + 1 > self.maximum_population:
                    print("Failed to add entity : Not enough space")
                    return False

                self.units.add(entity)
                self.population += 1
                return True
        return False

    def remove_member(self, entity):
        if entity.team == self.teamID:
            if isinstance(entity, Building):
                if entity in self.buildings:
                    self.buildings.remove(entity)
                    self.maximum_population -= entity.population
                    return True
            elif isinstance(entity, Unit):
                if entity in self.units:
                    self.units.remove(entity)
                    self.population -= 1
                    return True
        return False

    def modify_resources(self, Resources):
        """
        Modifie directement les ressources de l'équipe (ex: +100 gold, -50 wood, etc.).
        Note : appelle un refresh GUI.
        """
        self.resources['food'] += Resources.food 
        self.resources['wood'] += Resources.wood 
        self.resources['gold'] += Resources.gold
        game_map.game_state['player_info_updated'] = True
    
    def manage_creation(self, clock):
        """
        Gère la création de bâtiments/unités (self.en_cours).
        Une fois le temps écoulé => on les place dans .units ou .buildings.
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

        self.buildings.append(building)
        if hasattr(building, 'population'): #rajouter condition pour pas depasser MAXIMUM_POPULATION a 200
            self.maximum_population += building.population
        game_map.game_state['player_info_updated'] = True

        return True

    def battle(self,t,map,nb):
        """
        Attaque t, et l'adversaire défend.
        """
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
        """
        Attaque t, et l'adversaire ne défend pas.
        """
        i=0
        nb_soldier=0
        while(i<len(self.units) and nb_soldier< nb):
            soldier=self.units[i]
            if not(soldier.task) and not(isinstance(soldier,Villager)):
                nb_soldier+=1
                soldier.task=True
                if soldier.target:
                    soldier.attack(t,map)
            i+=1

    def modify_target(self,target,players_target):
        """
        Met à jour la cible de l'équipe (arrête toutes les attaques de la team)
        pour la remplacer par la nouvelle 'target'.
        """
        players_target[self.teamID]=target
        for unit in self.units:
            if not isinstance(unit,Villager):
                unit.target=None
                unit.task=True
                if unit.target:
                    unit.attack(target,map)

    def collectResource(self, villager, resource_tile, duration, game_map):
        """
        Méthode de récolte de ressources : villager se déplace et récolte sur 'resource_tile'.
        La quantité récoltée dépend de 'duration' et du 'resource_rate' du villager.
        """
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
        setattr(
            villager.resources,
            resource_tile.acronym.lower(),
            getattr(villager.resources, resource_tile.acronym.lower(), 0) + collected
        )
        
        resource_tile.storage = Resources(
            food=resource_tile.storage.food - (collected if resource_tile.acronym == "F" else 0),
            gold=resource_tile.storage.gold - (collected if resource_tile.acronym == "G" else 0),
            wood=resource_tile.storage.wood - (collected if resource_tile.acronym == "W" else 0),
        )
        
        if (resource_tile.storage.food <= 0 
            and resource_tile.storage.gold <= 0 
            and resource_tile.storage.wood <= 0):
            game_map.remove_entity(resource_tile, resource_tile.x, resource_tile.y)

        villager.task = False
        # ----------- AJOUT POUR METTRE A JOUR L'AFFICHAGE -----------
        game_map.game_state['player_info_updated'] = True
        # ------------------------------------------------------------

    def stockResources(self, villager, building, game_map):
        """
        Le villager va déposer ses ressources dans 'building' s'il le peut.
        """
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
        # On refresh l'UI
        game_map.game_state['player_info_updated'] = True
