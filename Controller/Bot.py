from Models.Team import *
#from Settings.setup import  RESOURCE_THRESHOLDS, UNIT_CLASSES, UNIT_TRAINING_MAP
from Entity.Unit import Villager
from Entity.Building import Building

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



#Priorité 2

def search_for_target(unit, enemy_team, attack_mode=True):
    """
    Searches for the closest enemy unit or building depending on the mode.
    vise en premier les keeps puis les units puis les villagers et buildings
    """
    closest_distance = float("inf")
    closest_entity = None

    targets=[keep for keep in enemy_team.buildings if isinstance(keep,Keep)]
    if targets!=[] and attack_mode:
        for enemy in targets:
            dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
            if attack_mode or not isinstance(enemy,Villager): 
                if dist < closest_distance:
                    closest_distance = dist
                    closest_entity = enemy
    if closest_entity!=None:
        unit.set_target(closest_entity)
        return unit.attack_target is not None

    targets=[unit for unit in enemy_team.units if not isinstance(unit,Villager)]
    for enemy in targets:
        dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
        if dist < closest_distance:
            closest_distance = dist
            closest_entity = enemy
    if closest_entity!=None:
        unit.set_target(closest_entity)
        return unit.attack_target is not None

    if attack_mode:
        targets=[unit for unit in enemy_team.units if isinstance(unit,Villager)]
        for enemy in targets:
            dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
            if attack_mode or not isinstance(enemy,Villager): 
                if dist < closest_distance:
                    closest_distance = dist
                    closest_entity = enemy
    
        for enemy_building in enemy_team.buildings:
            dist = math.dist((unit.x, unit.y), (enemy_building.x, enemy_building.y))
            if dist < closest_distance:
              closest_distance = dist
              closest_entity = enemy_building

    unit.set_target(closest_entity)
    return unit.attack_target is not None


def priority_2(players,selected_player,players_target):
    #lance l'attaque en essayant de choisir une cible
    #si elle réussi vise en premier les keeps ou les units
    if players_target[selected_player.teamID]!=None:
        #attaque déjà en cours
        return False
    return choose_target(players,selected_player,players_target)
        
def choose_target(players,selected_player,players_target):
    #testé
    count_max=201
    target=None
    for enemy_team in players:
        if enemy_team!=selected_player:
            count = sum(1 for unit in enemy_team.units if not isinstance(unit, Villager))
            if count<count_max:
                target=enemy_team
                count_max=count
    if target!=None:
        selected_player.modify_target(target,players_target)
    return target!=None

def is_under_attack():
    return True

def manage_battle(selected_player,players_target,players,game_map,dt):
    #réassigne une target a chaque unit d'un player lorsqu'il n'en a plus lors d'un combat attaque ou défense
    #arrete les combats
    enemy=players_target[selected_player.teamID]
    attack_mode=True
    #defense
    if is_under_attack():
    #on cherche la team qui est entrain de nous attaquer si les frontieres on été violer:
        for i in range(0,len(players_target)):
            if players_target[i]==selected_player:
                for team in players:
                    if team.teamID==i:
                            players_target[selected_player.teamID]=None
                            enemy=team
                            attack_mode=False
    if enemy!=None and (len(enemy.units)!=0 or len(enemy.buildings)!=0):
        for unit in selected_player.units:
            if not isinstance(unit,Villager) or (len(selected_player.units)==0 and not attack_mode):
                if unit.attack_target!=None and unit.attack_target.state!='death':
                    unit.seekAttack(game_map,dt)
                else:
                    search_for_target(unit,enemy,attack_mode)
    else:
        selected_player.modify_target(None,players_target)
    if get_military_unit_count(selected_player)==0:
        selected_player.modify_target(None,players_target)


