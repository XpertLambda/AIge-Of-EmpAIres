from collections import Counter
from Settings.setup import *
from Settings.entity_mapping import *
from Entity.Entity import *
from Entity.Building import *
from Entity.Unit import *
from Entity.Resource import Resource
from Models.Map import GameMap
from Controller.terminal_display_debug import debug_print

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
                    building_instance = building_class_map[building](team=teamID)
                    building_instance.processTime = building_instance.buildTime
                    self.add_member(building_instance)

        for unit, amount in difficulty_config[difficulty]['Units'].items():
            for _ in range(amount):
                if unit in unit_class_map:
                    unit_instance = unit_class_map[unit](team=teamID)
                    self.add_member(unit_instance)

    def add_member(self, entity):
        if entity.team == self.teamID :
            if entity in self.buildings or entity in self.units:
                return False

            if isinstance(entity, Building):
                if entity.population + self.maximum_population > MAXIMUM_POPULATION :
                    debug_print("Maximum population reached")
                    return False

                self.buildings.add(entity)
                self.maximum_population += entity.population
                debug_print(f'addded {entity} : {entity.entity_id} to team #{entity.team}')
                return True

            elif isinstance(entity, Unit):
                if self.population + 1 > self.maximum_population:
                    debug_print("Failed to add entity : Not enough space")
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

    def build(self, building, x, y, num_builders, game_map):
        building = building_class_map[building](team=self.teamID)
        x, y = round(x), round(y)
        if not self.resources.has_enough(building.cost.get()):
            del building
            return False

        builders = set()
        for unit in self.units:
            if unit.acronym == "v" and unit.isAvailable():
                builders.add(unit)
                if len(builders) == num_builders:
                    break
        if not builders:
            del building
            return False

        for i in range(building.size):
            for j in range(building.size):
                pos = (x + i, y + j)
                if pos in game_map.grid:
                    del building
                    return False

        if not game_map.add_entity(building, x, y):
            del building
            return False

        self.resources.decrease_resources(building.cost.get())

        for villager in builders:
            villager.set_task('build', building)

        building.set_builders(builders)

        return True
    '''   
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
            debug_print("No free villager found to build.")
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
                debug_print("ok")
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

        
    '''