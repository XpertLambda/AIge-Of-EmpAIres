# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\Decisonnode.py
# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\Decisonnode.py
from Controller.Bot import *
from Controller.terminal_display_debug import debug_print
from Entity.Building import Farm, Barracks, ArcheryRange, Stable, House, Camp, Keep
from Entity.Unit import Unit  # Import your Unit class
from Controller import Bot
class DecisionNode:
    def __init__(self, condition, true_branch=None, false_branch=None, action=None):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch
        self.action = action

    def evaluate(self):
        if self.condition():
            if self.true_branch:
                return self.true_branch.evaluate()
            elif self.action:
                return self.action()
        else:
            if self.false_branch:
                return self.false_branch.evaluate()
            elif self.action:
                return self.action()

# --- Conditions ---
def is_enemy_in_range_condition(bot, unit):
    """Checks if an enemy is within attack range of the unit."""
    if unit.attack_target and unit.attack_target.isAlive():
        distance = math.dist((unit.x, unit.y), (unit.attack_target.x, unit.attack_target.y))
        # Consider adding unit size to the range calculation for more accuracy
        return distance <= unit.attack_range
    return False

def can_attack_condition(unit):
    """Checks if the unit's attack is off cooldown."""
    return unit.attack_timer == 0

def has_target_condition(unit):
    """Checks if the unit has a target."""
    return unit.attack_target is not None and unit.attack_target.isAlive()

def is_enemy_building_in_range_condition(bot, unit):
    """Vérifie si un bâtiment ennemi est à portée de l'unité."""
    if unit.attack_target and isinstance(unit.attack_target, Building) and unit.attack_target.team != unit.team and unit.attack_target.isAlive():
        distance = math.dist((unit.x, unit.y), (unit.attack_target.x, unit.attack_target.y))
        return distance <= unit.attack_range
    return False

def is_unit_idle_condition(unit):
    """Checks if the unit is idle (no path and no target)."""
    return not unit.path and not unit.attack_target

def is_under_attack_condition(bot, enemy_team):
    return bot.is_under_attack(enemy_team)

# --- Actions ---

def find_enemy_target_action(bot, unit, enemy_teams, game_map):
    """Trouve une cible ennemie (unité ou bâtiment) pour l'unité."""
    debug_print(f"Unité {unit.entity_id}: Recherche de cible")
    if enemy_teams:
        enemy_team = enemy_teams[0]  # Focus sur la première équipe ennemie pour l'instant.
        closest_enemy = None
        min_distance = float('inf')

        # Chercher les unités ennemies en premier
        for enemy_unit in enemy_team.units:
            if enemy_unit.isAlive(): # Vérifier si l'unité ennemie est en vie
                distance = math.dist((unit.x, unit.y), (enemy_unit.x, enemy_unit.y))
                if distance < min_distance:
                    min_distance = distance
                    closest_enemy = enemy_unit

        # Si aucune unité ennemie, chercher les bâtiments ennemis
        if closest_enemy is None:
            for enemy_building in enemy_team.buildings:
                if enemy_building.isAlive(): # Vérifier si le bâtiment ennemi est en vie
                    distance = math.dist((unit.x, unit.y), (enemy_building.x, enemy_building.y))
                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = enemy_building

        unit.set_target(closest_enemy)  # Définir la cible.
        if closest_enemy:
            debug_print(f"Unité {unit.entity_id}: Cible acquise : {closest_enemy.entity_id}")

def move_to_enemy_action(unit, game_map):
    """Moves the unit towards its target."""
    if unit.attack_target:
        debug_print(f"Unit {unit.entity_id}: Moving to target")
        unit.set_destination((unit.attack_target.x, unit.attack_target.y), game_map)

def attack_enemy_action(unit):
    """Attacks the target enemy."""
    debug_print(f"Unit {unit.entity_id}: Attacking target")
    unit.attack_timer = 0  # Reset attack timer
    unit.attack_target.hp -= unit.attack_power
    if unit.attack_target.hp <= 0:
        unit.attack_target.kill() # Kill the target if HP drops to 0 or below
        unit.attack_target = None

def do_nothing_action(unit):
    """The unit does nothing."""
    debug_print(f"Unit {unit.entity_id}: Doing nothing")


# --- Decision Tree ---
def create_unit_combat_decision_tree(bot, unit, enemy_teams, game_map):
    """Decision tree for unit combat."""
    return DecisionNode(
        condition=lambda: has_target_condition(unit),
        true_branch=DecisionNode(
            condition=lambda: isinstance(unit.attack_target, Unit),  # Check if target is a Unit
            true_branch=DecisionNode(  # If it's a unit, handle unit attacks
                condition=lambda: is_enemy_in_range_condition(bot, unit),
                true_branch=DecisionNode(
                    condition=lambda: can_attack_condition(unit),
                    true_branch=DecisionNode(
                        condition = lambda: True,
                        action=lambda: attack_enemy_action(unit)
                    ),
                    false_branch=DecisionNode(
                        condition=lambda: True,
                        action=lambda: do_nothing_action(unit)
                    )
                ),
                false_branch=DecisionNode(
                    condition=lambda: True,
                    action=lambda: move_to_enemy_action(unit, game_map)
                )
            ),
            false_branch=DecisionNode(  # If it's NOT a unit (must be a building)
                condition=lambda: is_enemy_building_in_range_condition(bot, unit),
                true_branch=DecisionNode(
                    condition=lambda: can_attack_condition(unit),
                    true_branch=DecisionNode(
                        condition = lambda: True,
                        action=lambda: attack_enemy_action(unit)  # Attack the building
                    ),
                    false_branch=DecisionNode(
                        condition=lambda: True,
                        action=lambda: do_nothing_action(unit)
                    )
                ),
                false_branch=DecisionNode(
                    condition=lambda: True,
                    action=lambda: move_to_enemy_action(unit, game_map)  # Move towards the building
                )
            )
        )
    )
# --- Conditions ---
def is_under_attack_condition(bot, enemy_team):
    return bot.is_under_attack(enemy_team)

def is_resource_shortage_condition(bot):
    return bot.get_resource_shortage() is not None

def is_resource_shortage_condition_wood(bot):
    return bot.get_resource_shortage() == 'wood'

def is_resource_shortage_condition_gold(bot):
    return bot.get_resource_shortage() == 'gold'

def is_resource_shortage_condition_food(bot):
    return bot.get_resource_shortage() == 'food'

def are_buildings_needed_condition(bot):
    return bot.check_building_needs()

def are_economic_buildings_needed_condition(bot):
    needed_buildings = bot.check_building_needs()
    economic_buildings = ["Farm", "Camp", "House"] # Liste des bâtiments économiques
    return any(building in needed_buildings for building in economic_buildings)

def are_military_buildings_needed_condition(bot):
    needed_buildings = bot.check_building_needs()
    military_buildings = ["Barracks", "ArcheryRange", "Stable", "Keep"] # Liste des bâtiments militaires/défensifs
    return any(building in needed_buildings for building in military_buildings)

def are_defensive_buildings_needed_condition(bot):
    needed_buildings = bot.check_building_needs()
    defensive_buildings = ["Keep"]  # Liste des bâtiments défensifs (Keep)
    return any(building in needed_buildings for building in defensive_buildings)


def is_army_below_threshold_condition(bot):
    return bot.get_military_unit_count(bot.player_team) < 15 # Reduced threshold for example

def is_military_count_low_condition(bot):
    return bot.get_military_unit_count(bot.player_team) < 10 # Example threshold

def is_archer_count_low_condition(bot):
    return sum(1 for unit in bot.player_team.units if isinstance(unit, Archer)) < 5

def is_swordsman_count_low_condition(bot):
    return sum(1 for unit in bot.player_team.units if isinstance(unit, Swordsman)) < 5

def is_horseman_count_low_condition(bot):
    return sum(1 for unit in bot.player_team.units if isinstance(unit, Horseman)) < 3


def are_damaged_buildings_condition(bot):
    return len(bot.get_critical_points()) > 0

# --- Actions ---
def allocate_villagers_to_resource_action(self, resource_type, villager):
        """Allocates a specific villager to gather a specific resource."""
        

        resource_locations = self.find_resource(resource_type)  # Use the find_resource method
        if resource_locations:
            nearest_drop_point = self.find_nearest_drop_point(villager)
            closest_resource = min(
                resource_locations,
                key=lambda pos_entity: math.dist((nearest_drop_point.x, nearest_drop_point.y), pos_entity[0])
            )
            villager.set_target(closest_resource[1])  # Set the target to the Resource object
            villager.state = 'gather'
            
        else:
            debug_print(f"No {resource_type} resources found!")

def build_economic_structure_action(self):
    """Attempts to build a necessary economic structure (e.g., Farm)."""
    if self.can_build_building(Farm):
        self.buildBuilding(Farm(team=self.player_team.teamID), self.clock, 1, self.game_map)
        return True
    return False

def build_military_structure_action(self):
    """Attempts to build a necessary military structure (e.g., Barracks)."""
    if self.can_build_building(Barracks):
        self.buildBuilding(Barracks(team=self.player_team.teamID), self.clock, 3, self.game_map)
        return True
    elif self.can_build_building(ArcheryRange):
        self.buildBuilding(ArcheryRange(team=self.player_team.teamID), self.clock, 3, self.game_map)
        return True
    elif self.can_build_building(Stable):
        self.buildBuilding(Stable(team=self.player_team.teamID), self.clock, 3, self.game_map)
        return True
    return False

def defend_action(bot, enemy_team, players_target, game_map, dt):
    debug_print("Decision Node Action: Defend under attack.")
    bot.priorty1(enemy_team, players_target,game_map, dt) # Using priority 1 for defense

def address_resource_shortage_action(bot):
    debug_print("Decision Node Action: Addressing resource shortage.")
    bot.priorty7() # Using priority 7 for resource management

def build_needed_structure_action(bot):
    debug_print("Decision Node Action: Building needed structures.")
    bot.build_structure(bot.clock) # Build structure action

def balance_army_action(bot):
    debug_print("Decision Node Action: Balancing army units.")
    bot.balance_units() # Balance units action

def repair_buildings_action(bot):
    debug_print("Decision Node Action: Repairing damaged buildings.")
    # Assuming priority_6 is for repair as per your initial request
    # if priority_6 action is not defined in Bot.py please check and adapt or replace with relevant repair logic
    pass # bot.priority_6() # Repair buildings action - adapt if needed

def manage_offense_action(bot, players, selected_player, players_target, game_map, dt):
    debug_print("Decision Node Action: Managing battle offensively.")
    bot.manage_battle(selected_player, players_target, players, game_map, dt) # Offensive battle management

def build_farm_action(bot):
    debug_print("Decision Node Action: Build Farm.")
    bot.buildBuilding(Farm(team=bot.player_team.teamID), bot.clock, 3, bot.game_map)

def build_barracks_action(bot):
    debug_print("Decision Node Action: Build Barracks.")
    bot.buildBuilding(Barracks(team=bot.player_team.teamID), bot.clock, 3, bot.game_map)

def build_archery_range_action(bot):
    debug_print("Decision Node Action: Build Archery Range.")
    bot.buildBuilding(ArcheryRange(team=bot.player_team.teamID), bot.clock, 3, bot.game_map)

def build_stable_action(bot):
    debug_print("Decision Node Action: Build Stable.")
    bot.buildBuilding(Stable(team=bot.player_team.teamID), bot.clock, 3, bot.game_map)

def build_house_action(bot):
    debug_print("Decision Node Action: Build House.")
    bot.buildBuilding(House(team=bot.player_team.teamID), bot.clock, 3, bot.game_map)

def build_camp_action(bot):
    debug_print("Decision Node Action: Build Camp.")
    bot.buildBuilding(Camp(team=bot.player_team.teamID), bot.clock, 3, bot.game_map)

def build_keep_action(bot):
    debug_print("Decision Node Action: Build Keep.")
    bot.buildBuilding(Keep(team=bot.player_team.teamID), bot.clock, 3, bot.game_map)

def train_villager_action(bot):
    debug_print("Decision Node Action: Train Villager.")
    bot.train_units(Villager)

def train_archer_action(bot):
    debug_print("Decision Node Action: Train Archer.")
    bot.train_units(Archer)

def train_swordsman_action(bot):
    debug_print("Decision Node Action: Train Swordsman.")
    bot.train_units(Swordsman)

def train_horseman_action(bot):
    debug_print("Decision Node Action: Train Horseman.")
    bot.train_units(Horseman)

def allocate_villagers_to_wood_action(bot):
    debug_print("Decision Node Action: Allocate Villagers to Wood.")
    bot.reallocate_villagers('wood')

def allocate_villagers_to_gold_action(bot):
    debug_print("Decision Node Action: Allocate Villagers to Gold.")
    bot.reallocate_villagers('gold')

def allocate_villagers_to_food_action(bot):
    debug_print("Decision Node Action: Allocate Villagers to Food.")
    bot.reallocate_villagers('food')


# --- Decision Trees ---

def create_economic_decision_tree(bot, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target):
    """Decision tree for Economic mode - prioritizes resource gathering and building."""
    return DecisionNode(
        condition=lambda: is_under_attack_condition(bot, enemy_team),
        true_branch=DecisionNode(
            condition=lambda: True,
            action=lambda: defend_action(bot, enemy_team, players_target, game_map, dt)
        ),
        false_branch=DecisionNode(
            condition=lambda: is_resource_shortage_condition_gold(bot),
            true_branch=DecisionNode(
                condition=lambda: True,
                action=lambda: bot.allocate_villagers_to_resource_action('gold', Villager)
            ),
            false_branch=DecisionNode(
                condition=lambda: is_resource_shortage_condition_wood(bot),
                true_branch=DecisionNode(
                    condition=lambda: True,
                    action=lambda: bot.allocate_villagers_to_resource_action('wood',Villager)
                ),
                false_branch=DecisionNode(
                    condition=lambda: are_economic_buildings_needed_condition(bot),
                    true_branch=DecisionNode(
                        condition=lambda: True,
                        action=lambda: build_economic_structure_action(bot)  # Build economic structures (e.g., farms)
                    ),
                    false_branch=DecisionNode(
                        condition=lambda: are_military_buildings_needed_condition(bot), 
                        true_branch=DecisionNode(
                            condition=lambda: True,
                            action=lambda: build_military_structure_action(bot)  # Build essential military structures
                        ),
                        false_branch=DecisionNode(
                            condition=lambda: is_military_count_low_condition(bot),
                            true_branch=DecisionNode(
                                condition=lambda: True,
                                action=lambda: balance_army_action(bot)  # Train basic military units for defense
                            ),
                            false_branch=DecisionNode(
                                condition=lambda: True,
                                action=lambda: do_nothing_action(bot)  # If everything is fine, do nothing
                            )
                        )
                    )
                )
            )
        )
    )

def create_defensive_decision_tree(bot, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target):
    """Decision tree for Defensive mode - focuses on defense and strong economy, builds defensive structures and army."""
    return DecisionNode(
        condition=lambda: is_under_attack_condition(bot, enemy_team),
        true_branch=DecisionNode(
            condition=lambda: True,
            action=lambda: defend_action(bot, enemy_team, players_target, game_map, dt)
        ),
        false_branch=DecisionNode(
            condition=lambda: are_damaged_buildings_condition(bot),
            true_branch=DecisionNode(
                condition=lambda: True,
                action=lambda: repair_buildings_action(bot)
            ),
            false_branch=DecisionNode(
                condition=lambda: are_defensive_buildings_needed_condition(bot),
                true_branch=DecisionNode(
                    condition=lambda: True,
                    action=lambda: build_keep_action(bot)
                ),
                false_branch=DecisionNode(
                    condition=lambda: is_resource_shortage_condition_wood(bot),
                    true_branch=DecisionNode(
                        condition=lambda: True,
                        action=lambda: allocate_villagers_to_wood_action(bot)
                    ),
                    false_branch=DecisionNode(
                        condition=lambda: is_military_count_low_condition(bot),
                        true_branch=DecisionNode(
                            condition=lambda: True,
                            action=lambda: balance_army_action(bot)
                        ),
                        false_branch=DecisionNode(
                            condition=lambda: is_resource_shortage_condition_food(bot),
                            true_branch=DecisionNode(
                                condition=lambda: True,
                                action=lambda: allocate_villagers_to_food_action(bot)
                            ),
                            false_branch=DecisionNode(
                                condition=lambda: True,
                                action=lambda: build_economic_structure_action(bot)  # Build economic structures (e.g., Farm)
                            )
                        )
                    )
                )
            )
        )
    )

def create_offensive_decision_tree(bot, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target):
    """Decision tree for Offensive mode - focuses on aggressive military actions, builds army and attacks frequently."""
    return DecisionNode(
        condition=lambda: is_under_attack_condition(bot, enemy_team),
        true_branch=DecisionNode(
            condition=lambda: True,
            action=lambda: defend_action(bot, enemy_team, players_target, game_map, dt)
        ),
        false_branch=DecisionNode(
            condition=lambda: is_army_below_threshold_condition(bot),
            true_branch=DecisionNode(
                condition=lambda: is_resource_shortage_condition_wood(bot),
                true_branch=DecisionNode(
                    condition=lambda: True,
                    action=lambda: allocate_villagers_to_wood_action(bot)
                ),
                false_branch=DecisionNode(
                    condition=lambda: is_military_count_low_condition(bot),
                    action=lambda: balance_army_action(bot)
                )
            ),
            false_branch=DecisionNode(
                condition=lambda: are_military_buildings_needed_condition(bot),
                true_branch=DecisionNode(
                    condition=lambda: is_resource_shortage_condition_wood(bot),
                    true_branch=DecisionNode(
                        condition=lambda: True,
                        action=lambda: allocate_villagers_to_wood_action(bot)
                    ),
                    false_branch=DecisionNode(
                        condition=lambda: True,
                        action=lambda: build_military_structure_action(bot)
                    )
                ),
                false_branch=DecisionNode(
                    condition=lambda: is_resource_shortage_condition_gold(bot),
                    action=lambda: manage_offense_action(bot, players, selected_player, players_target, game_map, dt)
                )
            )
        )
    )

def create_default_decision_tree(bot, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target):
    """Fallback decision tree - a balanced approach, good for general gameplay."""
    return DecisionNode(
        condition=lambda: is_under_attack_condition(bot, enemy_team),
        true_branch=DecisionNode(
            condition=lambda: True,
            action=lambda: defend_action(bot, enemy_team, players_target, game_map, dt)
        ),
        false_branch=DecisionNode(
            condition=lambda: is_resource_shortage_condition_wood(bot),
            true_branch=DecisionNode(
                action=lambda: allocate_villagers_to_wood_action(bot)
            ),
            false_branch=DecisionNode(
                condition=lambda: is_resource_shortage_condition_food(bot),
                true_branch=DecisionNode(
                    action=lambda: allocate_villagers_to_food_action(bot)
                ),
                false_branch=DecisionNode(
                    condition=lambda: is_resource_shortage_condition_gold(bot),
                    true_branch=DecisionNode(
                        action=lambda: allocate_villagers_to_gold_action(bot)
                    ),
                    false_branch=DecisionNode(
                        condition=lambda: are_economic_buildings_needed_condition(bot),
                        true_branch=DecisionNode(
                            action=lambda: build_economic_structure_action(bot)
                        ),
                        false_branch=DecisionNode(
                            condition=lambda: are_military_buildings_needed_condition(bot),
                            true_branch=DecisionNode(
                                action=lambda: build_military_structure_action(bot)
                            ),
                            false_branch=DecisionNode(
                                condition=lambda: is_military_count_low_condition(bot),
                                true_branch=DecisionNode(
                                    action=lambda: balance_army_action(bot)
                                ),
                                false_branch=DecisionNode(
                                    condition=lambda: True,
                                    action=lambda: manage_offense_action(bot, players, selected_player, players_target, game_map, dt)
                                )
                            )
                        )
                    )
                )
            )
        )
    )