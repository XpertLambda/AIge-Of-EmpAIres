from Entity.Unit import Villager
from Entity.Building import Building
#Priorité 5

def get_military_unit_count(player_team):
    return sum(1 for unit in player_team.units if not (isinstance(unit, Villager) or isinstance(unit, Building)))


def train_units(player_team, unit_type, unit_cost):
    if can_train_unit(player_team, unit_cost, player_team.maximum_population):
        player_team.resources["gold"] -= unit_cost["gold"]
        player_team.resources["food"] -= unit_cost["food"]
        player_team.units.append(unit_type())
        print(f"Unité {unit_type.__name__} formée.")

def balance_units(player_team):
    villager_count = sum(1 for unit in player_team.units if isinstance(unit, Villager))
    military_count = get_military_unit_count(player_team)
    if player_team.resources["food"] < 100 and villager_count < 10:
        train_units(player_team, Villager, {"gold": 0, "food": 50})
    elif military_count < 20:
        train_units(player_team, MilitaryUnit, {"gold": 50, "food": 50})

def maintain_army(player_team):
    military_count = get_military_unit_count(player_team)
    if military_count < 20:
        balance_units(player_team)

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
        if isinstance(villager, Villager) and not villager.task:
            villager.repair(building)
            print(f"Villageois assigné à la réparation de {building}.")
            return True
    print("Aucun villageois disponible pour réparer.")
    return False

def repair_critical_buildings(player_team):
    damaged_buildings = get_damaged_buildings(player_team)
    for building in damaged_buildings:
        repair_cost = {"wood": 50} # Exemple de coût de réparation
        if can_repair_building(player_team, repair_cost):
            if not assign_villager_to_repair(player_team, building):
                print("Réparation différée faute de ressources ou de main-d'œuvre.")


