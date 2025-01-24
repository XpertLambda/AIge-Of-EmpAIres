from Models.Team import *
from Settings.setup import  RESOURCE_THRESHOLDS
from Entity.Unit import Villager, Archer, Swordsman, Horseman
from Entity.Building import Building, add_to_training_queue

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

def get_resource_shortage(current_resources, RESOURCE_THRESHOLDS=RESOURCE_THRESHOLDS):
    # Access the specific resource attributes from the Resources object
    if current_resources.food < RESOURCE_THRESHOLDS['food']:
        return 'food'
    if current_resources.wood < RESOURCE_THRESHOLDS['wood']:
        return 'wood'
    if current_resources.gold < RESOURCE_THRESHOLDS['gold']:
        return 'gold'
    return None
def find_resource_location(game_map, resource_acronym):
    for (x, y), cell_content in game_map.grid.items():
        if resource_acronym in cell_content:
            return (x, y)  


def reallocate_villagers(resource_in_shortage, villagers, game_map):
    for villager in villagers:
        if villager.isAvailable() and not villager.task:
            for x, y in game_map.grid:
                resource_nodes = game_map.grid[(x, y)]
                for resource_node in resource_nodes:
                    if resource_node.acronym.lower() == resource_in_shortage[0].lower():
                        villager.set_target(resource_node)
                        return


def check_and_address_resources(team, game_map, thresholds):
    resource_shortage = get_resource_shortage(team.resources, thresholds)
    if resource_shortage:
        reallocate_villagers(resource_shortage, team.units, game_map)
    
        
# AI resource management Logic

# 1. Monitor resource levels for shortages
# - Use the current resource levels and predefined thresholds.
# - Identify if any resource is below its threshold.

# 2. Reallocate villagers to address resource shortages
# - Find idle villagers or villagers collecting less critical resources.
# - Assign them to collect the resource in shortage.
# - Ensure villagers are directed to the closest available resource node.

# 3. Integrate into the game loop
# - Periodically check resource levels and act accordingly.
# - Address shortages by reallocating villagers.

