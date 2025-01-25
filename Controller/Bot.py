from Models.Team import *
from Settings.setup import  RESOURCE_THRESHOLDS, UNIT_CLASSES, UNIT_TRAINING_MAP
from Entity.Unit import Villager, Archer, Swordsman, Horseman
from Entity.Building import *


#Priorité 5

def get_military_unit_count(player_team):
    print(f"MUC : {sum(1 for unit in player_team.units if not isinstance(unit, Villager))}")

    return sum(1 for unit in player_team.units if not isinstance(unit, Villager))
    

def train_units(player_team, building):
    return building.add_to_training_queue(player_team)

def balance_units(player_team):
    villager_count = sum(1 for unit in player_team.units if isinstance(unit, Villager))
    military_count = get_military_unit_count(player_team)
    if player_team.resources.food < 100 and villager_count < 10:
        train_units(player_team, Villager, {"gold": 0, "food": 50})
    elif military_count < 20:
        train_units(player_team, (unit for unit in player_team.units if not isinstance(unit, Villager)), {"gold": 50, "food": 50})
    for b in player_team.buildings:
        train_units(player_team,b)

def choose_attack_composition(player_team):
    archers = [unit for unit in player_team.units if isinstance(unit, Archer)]
    swordsmen = [unit for unit in player_team.units if isinstance(unit, Swordsman)]
    horsemen = [unit for unit in player_team.units if isinstance(unit, Horseman)]

    if len(archers) >= 3 and len(swordsmen) >= 1 and len(horsemen) >= 1:
        return archers[:3] + swordsmen[:1] + horsemen[:1]
    elif len(archers) >= 3 and len(swordsmen) >= 1:
        return archers[:3] + swordsmen[:1]
    elif len(archers) >= 3:
        return archers[:3]
    elif len(swordsmen) >= 1:
        return swordsmen[:1]
    elif len(horsemen) >= 1:
        return horsemen[:1]
    else:
        return []

def maintain_army(player_team):
    military_count = get_military_unit_count(player_team)
    if military_count < 20:
        balance_units(player_team)
    else:
        attack_composition = choose_attack_composition(player_team)
        for unit in attack_composition:
            if not isinstance(unit, Villager):
                if unit.idle:
                    unit.seek_attack()
                elif unit.target:
                    unit.kill()
                else:
                    unit.setIdle()
                    
def priorite_5(player_team,unit,building):
    train_units(player_team,unit,building)
    balance_units(player_team)
    choose_attack_composition(player_team)
    maintain_army(player_team)

#Priorty seven avoid ressources shortage 

def get_resource_shortage(current_resources, RESOURCE_THRESHOLDS):
    for resource in ['food', 'wood', 'gold']:
        if getattr(current_resources, resource, 0) < RESOURCE_THRESHOLDS.get(resource, 0):
            return resource
def get_resource_shortage(current_resources, RESOURCE_THRESHOLDS):
    for resource in ['food', 'wood', 'gold']:
        if getattr(current_resources, resource, 0) < RESOURCE_THRESHOLDS.get(resource, 0):
            return resource
    return None


def find_resources(game_map, resource_type):
    if not resource_type:
        return []
    resource_positions = []
    for position, entities in game_map.grid.items():
        for entity in entities:
            if isinstance(entity, resource_type):
                resource_positions.append(position)
    return resource_positions


def find_resources(game_map, resource_type):
    if not resource_type:
        return []
    resource_positions = []
    for position, entities in game_map.grid.items():
        for entity in entities:
            if isinstance(entity, resource_type):
                resource_positions.append(position)
    return resource_positions


def reallocate_villagers(resource_in_shortage, team, game_map):
    for unit in team.units:  # Assuming `team.units` provides access to all units in the team
        if hasattr(unit, "carry") and unit.isAvailable() and not unit.task:
            resource_positions = find_resources(game_map, resource_in_shortage)
            if resource_positions:
                nearest_resource = min(
                    resource_positions,
                    key=lambda pos: math.sqrt((unit.x - pos[0]) ** 2 + (unit.y - pos[1]) ** 2)
                )
                unit.set_target(nearest_resource)
                return


def check_and_address_resources(team, game_map, RESOURCE_THRESHOLDS):
    resource_shortage = get_resource_shortage(team.resources, RESOURCE_THRESHOLDS)
    if resource_shortage:
        reallocate_villagers(resource_shortage, team, game_map)

    
 

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