from Models.Team import *
from Settings.setup import  RESOURCE_THRESHOLDS
from Entity.Unit import Villager, Archer, Swordsman, Horseman
from Entity.Building import *


#Priorité 5

def get_military_unit_count(player_team):
    #print(f"MUC : {sum(1 for unit in player_team.units if not isinstance(unit, Villager))}")

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


def get_resource_shortage(self):
        RESOURCE_MAPPING ={
        "food": Farm,
        "wood": Tree,
        "gold": Gold,
        }
        # Assume `self.player_team.resources.get()` returns a tuple of resource quantities
        resource_quantities = self.player_team.resources.get()  # Fetch the tuple
        resource_keys = list(RESOURCE_THRESHOLDS.keys())  # Get the order of resources
        
        shortages = {}
        for i, key in enumerate(resource_keys):
            # Ensure the index does not exceed the length of resource_quantities
            resource_amount = resource_quantities[i] if i < len(resource_quantities) else 0
            shortages[key] = RESOURCE_THRESHOLDS[key] - resource_amount

        critical_shortage = RESOURCE_MAPPING.key(min(shortages, key=shortages.get))
        return critical_shortage if shortages[critical_shortage] > 0 else None




def reallocate_villagers(self, resource_type):
        """
        Reallocates Villagers to address resource shortages.
        """
        for villager in self.player_team.units:
            if isinstance(villager, Villager) and villager.isAvailable():
                nearest_drop_point = min(
                    (b for b in self.player_team.buildings if hasattr(b, " resourceDropPoint=True")),
                    key=lambda dp: math.dist((villager.x, villager.y), (dp.x, dp.y)),
                    default=None
                )
                if nearest_drop_point:
                    resource_positions = [
                        pos for pos, set in self.game_map.resources.items()
                        if isinstance(set, resource_type)
                    ]
                    if resource_positions:
                        nearest_resource = min(
                            resource_positions,
                            key=lambda pos: math.dist(
                                (nearest_drop_point.x, nearest_drop_point.y), pos
                            )
                        )
                        l=self.game_map.get(nearest_resource)
                        resource_target = next((entity for entity in l if isinstance(entity, resource_type)), None)
                        villager.set_target(resource_target)
                        return



def priorty7(self, RESOURCE_THRESHOLDS=RESOURCE_THRESHOLDS):
    resource_shortage = get_resource_shortage(self, RESOURCE_THRESHOLDS)
    if resource_shortage:
        reallocate_villagers(resource_shortage,self)



#Priorité 2

def search_for_target(unit, enemy_team, attack_mode=True):

    """
    Searches for the closest enemy unit or building depending on the mode.
    vise en premier les keeps puis les units puis les villagers et buildings
    """
    if enemy_team==None:
        return
    closest_distance = float("inf")
    closest_entity = None
    keeps=[keep for keep in enemy_team.buildings if isinstance(keep,Keep)]  
    targets=[unit for unit in enemy_team.units if not isinstance(unit,Villager)]

    for enemy in targets:
        dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
        if dist < closest_distance:
            closest_distance = dist
            closest_entity = enemy
    if attack_mode and closest_entity==None:
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

    if attack_mode:
        for enemy in keeps:
            dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
            if attack_mode or not isinstance(enemy,Villager): 
                if dist < closest_distance:
                    closest_distance = dist
                    closest_entity = enemy 
    if closest_entity!=None:
        if keeps!=[] and attack_mode:
            for keep in keeps:
                dist=math.dist((keep.x,keep.y),(closest_entity.x,closest_entity.y))
                if dist<keep.attack_range:
                    closest_entity=keep
    
    unit.set_target(closest_entity)
    return unit.attack_target is not None



def priority_2(players,selected_player,players_target):
    #lance l'attaque en essayant de choisir une cible
    #si elle réussi vise en premier les keeps ou les units
    if players_target[selected_player.teamID]!=None:
        #attaque déjà en cours
        return False
    return choose_target(players,selected_player,players_target)


def modify_target(player,target,players_target):
    """
    Met à jour la cible de l'équipe (arrête toutes les attaques de la team)
    pour la remplacer par la nouvelle 'target'.
    """
    players_target[player.teamID]=target
    for unit in player.units:
        unit.set_target(None)
        
def choose_target(players,selected_player,players_target):
    count_max=300
    target=None
    for enemy_team in players:
        if enemy_team!=selected_player:
            count = sum(1 for unit in enemy_team.units if not isinstance(unit, Villager))
            count+=sum(1 for building in enemy_team.buildings if not isinstance(building, Keep ))
            if count<count_max:
                target=enemy_team
                count_max=count
    if target!=None:
        modify_target(selected_player,target,players_target)
    return target!=None


def manage_battle(selected_player,players_target,players,game_map,dt):
    #réassigne une target a chaque unit d'un player lorsqu'il n'en a plus lors d'un combat attaque ou défense
    #arrete les combats
    enemy=players_target[selected_player.teamID]
    attack_mode=True
    #defense
    #if any([is_under_attack(selected_player,enemy_team) for enemy_team in players]):
    if True:
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
                if unit.attack_target==None or not unit.attack_target.isAlive():
                    search_for_target(unit,enemy,attack_mode)
    else:
        modify_target(selected_player,None,players_target)
    if get_military_unit_count(selected_player)==0:
        modify_target(selected_player,None,players_target)


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

def priorty_6(player_team):
    damaged_buildings = get_damaged_buildings(player_team)
    for building in damaged_buildings:
        repair_cost = {"wood": 50} 
        if can_repair_building(player_team, repair_cost):
            if not assign_villager_to_repair(player_team, building):
                print("Réparation différée faute de ressources ou de main-d'œuvre.")

#Priority_1

#Priority_1
ATTACK_RADIUS = 5


def is_under_attack(self, enemy_team, ):
    zone=self.team.zone.get_zone()

    for z in zone:
     entities = game_map.get(z)  # Get the list of entities in the zone
    for entity in entities:
        if entity in enemy_team.units:
            return True
    return False




def gather_units_for_defense(self,  enemy_team):
    critical_points = sorted(self.get_damaged_buildings(critical_threshold=0.7))
    for point in critical_points:
        for unit in self.units:
            if not hasattr(unit, 'carry') and not unit.target:
                target = search_for_target(unit, enemy_team, attack_mode=False)
                if target:
                    unit.set_target(target)
                else:
                    unit.set_destination((point.x, point.y))



def build_defensive_structure(self, building_type,  num_builders):
    critical_points= sorted(self.get_damaged_buildings(critical_threshold=0.7))
    if critical_points:
        for point in critical_points:
             self.team.build(building_type, point.x, point.y ,num_builders,self.game_map)
                

   
        

def defend_under_attack(self, enemy_team, players_target,  dt):
    if is_under_attack(self, enemy_team):
        critical_points = sorted(self.get_damaged_buildings(critical_threshold=0.7))
        modify_target(self, None, players_target)
        gather_units_for_defense(self,  enemy_team)
        
        balance_units(self)
        
        build_defensive_structure(self, "Keep", 3)
        manage_battle(selected_player,None,players,game_map,dt)

def priorty1(self, enemy_team, players_target, game_map, dt):
    if is_under_attack(self, enemy_team):
        defend_under_attack(self, enemy_team, players_target, game_map, dt)