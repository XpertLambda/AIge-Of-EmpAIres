from Models.Team import *
from Settings.setup import  RESOURCE_THRESHOLDS, UNIT_CLASSES, UNIT_TRAINING_MAP
from Entity.Unit import Villager
from Entity.Building import *

#Priorité 5

def get_military_unit_count(player_team):
    return sum(1 for unit in player_team.units if not isinstance(unit, Villager))


def train_units(player_team, unit):
    if add_to_training_queue(player_team):
        player_team.resources["gold"] -= unit.cost.gold
        player_team.resources["food"] -= unit.cost.food
        player_team.units.append(unit())
        print(f"Unité {unit.__name__} formée.")

def balance_units(player_team):
    villager_count = sum(1 for unit in player_team.units if isinstance(unit, Villager))
    military_count = get_military_unit_count(player_team)
    if player_team.resources["food"] < 100 and villager_count < 10:
        train_units(player_team, Villager, {"gold": 0, "food": 50})
    elif military_count < 20:
        train_units(player_team, (unit for unit in player_team.unites if not isinstance(unit, Villager)), {"gold": 50, "food": 50})

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

#Priorité 6

def get_damaged_buildings(player_team, critical_threshold=0.5):
    return [
        building for building in player_team.buildings
        if building.hp / building.max_hp < critical_threshold
    ]

def can_repair_building(player_team, repair_cost):
    return player_team.resources["wood"] >= repair_cost["wood"]

def assign_villager_to_repair(player_team, building):
    for villager in player_team.units:
        if isinstance(villager, Villager) and villager.isAvailable():
            villager.repair(building)
            print(f"Villageois assigné à la réparation de {building}.")
            return True
    print("Aucun villageois disponible pour réparer.")
    return False

def repair_critical_buildings(player_team):
    damaged_buildings = get_damaged_buildings(player_team)
    for building in damaged_buildings:
        repair_cost = {"wood": 50} 
        if can_repair_building(player_team, repair_cost):
            if not assign_villager_to_repair(player_team, building):
                print("Réparation différée faute de ressources ou de main-d'œuvre.")

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