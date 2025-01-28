# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\Decisonnode.py
# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\Decisonnode.py
from Controller.Bot import *
from Controller.terminal_display_debug import debug_print
from Entity.Building import Farm, Barracks, ArcheryRange, Stable, House, Camp, Keep

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
def defend_action(bot, enemy_team, players_target, game_map, dt):
    debug_print("Decision Node Action: Defend under attack.")
    bot.priorty1(enemy_team, players_target, dt) # Using priority 1 for defense

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
    """Decision tree for Economic mode - focuses on economy, defends if attacked."""
    return DecisionNode(
        condition=lambda: is_under_attack_condition(bot, enemy_team),
        true_branch=DecisionNode(
            condition=lambda: True,  # Always execute the defense action if under attack
            action=lambda: defend_action(bot, enemy_team, players_target, game_map, dt)
        ),
        false_branch=DecisionNode(
            condition=lambda: is_resource_shortage_condition_wood(bot),
            true_branch=DecisionNode(
                condition=lambda: True,
                action=lambda: allocate_villagers_to_wood_action(bot)
            ),
            false_branch=DecisionNode(
                condition=lambda: is_resource_shortage_condition_food(bot),
                true_branch=DecisionNode(
                    condition=lambda: True,
                    action=lambda: allocate_villagers_to_food_action(bot)
                ),
                false_branch=DecisionNode(
                    condition=lambda: is_resource_shortage_condition_gold(bot),
                    true_branch=DecisionNode(
                        condition=lambda: True,
                        action=lambda: allocate_villagers_to_gold_action(bot)
                    ),
                    false_branch=DecisionNode(
                        condition=lambda: are_economic_buildings_needed_condition(bot),
                        true_branch=DecisionNode(
                            condition=lambda: True,
                            action=lambda: build_farm_action(bot)
                        ),
                        false_branch=DecisionNode(
                            condition=lambda: are_buildings_needed_condition(bot),
                            true_branch=DecisionNode(
                                condition=lambda: True,
                                action=lambda: build_house_action(bot)
                            ),
                            false_branch=DecisionNode(
                                condition=lambda: True,
                                action=lambda: balance_army_action(bot)
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
            condition=lambda: True,  # Always execute defense when under attack
            action=lambda: defend_action(bot, enemy_team, players_target, game_map, dt)
        ),
        false_branch=DecisionNode(
            condition=lambda: are_damaged_buildings_condition(bot),
            true_branch=DecisionNode(
                condition=lambda: True,  # Always repair if buildings damaged
                action=lambda: repair_buildings_action(bot)
            ),
            false_branch=DecisionNode(
                condition=lambda: are_defensive_buildings_needed_condition(bot),
                true_branch=DecisionNode(
                    condition=lambda: True,  # Always build defense if needed
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
                                action=lambda: build_farm_action(bot)
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
            action=lambda: defend_action(bot, enemy_team, players_target, game_map, dt) # Défend si attaqué en premier
        ),
        false_branch=DecisionNode(
            condition=lambda: is_army_below_threshold_condition(bot), # Priorité à l'armée offensive
            true_branch=DecisionNode(
                condition=lambda: is_resource_shortage_condition_wood(bot), # Assurer bois pour bâtiments militaires
                true_branch=DecisionNode(
                    action=lambda: allocate_villagers_to_wood_action(bot) # Allouer bois
                ),
                false_branch=DecisionNode(
                    action=lambda: balance_army_action(bot) # Construire armée si petite
                )
            ),
            false_branch=DecisionNode( # Si armée de taille décente, attaquer!
                condition=lambda: are_military_buildings_needed_condition(bot), # Vérifier bâtiments militaires
                true_branch=DecisionNode(
                    condition=lambda: is_resource_shortage_condition_wood(bot), # Assurer bois pour bâtiments militaires
                    true_branch=DecisionNode(
                        action=lambda: allocate_villagers_to_wood_action(bot) # Allouer bois
                    ),
                    false_branch=DecisionNode(
                        action=lambda: build_barracks_action(bot) # Construire casernes si besoin
                    ),
                ),
                false_branch=DecisionNode( # Si bâtiments militaires OK, attaquer
                    action=lambda: manage_offense_action(bot, players, selected_player, players_target, game_map, dt) # Gérer bataille offensive
                )
            )
        )
    )

def create_default_decision_tree(bot, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target):
    """Fallback decision tree - a balanced approach, good for general gameplay."""
    return DecisionNode(
        condition=lambda: is_under_attack_condition(bot, enemy_team),
        true_branch=DecisionNode(
            action=lambda: defend_action(bot, enemy_team, players_target, game_map, dt) # Défendre en cas d'attaque
        ),
        false_branch=DecisionNode(
            condition=lambda: is_resource_shortage_condition_wood(bot), # Vérifier pénurie de bois en premier
            true_branch=DecisionNode(
                action=lambda: allocate_villagers_to_wood_action(bot) # Allouer villageois au bois
            ),
            false_branch=DecisionNode(
                condition=lambda: is_resource_shortage_condition_food(bot), # Puis nourriture
                true_branch=DecisionNode(
                    action=lambda: allocate_villagers_to_food_action(bot) # Allouer villageois nourriture
                ),
                false_branch=DecisionNode(
                    condition=lambda: is_resource_shortage_condition_gold(bot), # Puis or
                    true_branch=DecisionNode(
                        action=lambda: allocate_villagers_to_gold_action(bot) # Allouer villageois or
                    ),
                    false_branch=DecisionNode(
                        condition=lambda: are_economic_buildings_needed_condition(bot), # Vérifier bâtiments économiques
                        true_branch=DecisionNode(
                            action=lambda: build_farm_action(bot) # Construire fermes si besoin
                        ),
                        false_branch=DecisionNode(
                            condition=lambda: are_military_buildings_needed_condition(bot), # Vérifier bâtiments militaires ensuite
                            true_branch=DecisionNode(
                                action=lambda: build_barracks_action(bot) # Construire casernes si besoin
                            ),
                            false_branch=DecisionNode( # Si bâtiments OK, équilibrer armée
                                condition=lambda: is_military_count_low_condition(bot),
                                true_branch=DecisionNode(
                                    action=lambda: balance_army_action(bot) # Équilibrer armée si faible
                                ),
                                false_branch=DecisionNode( # Si tout va bien, gérer offensive
                                    action=lambda: manage_offense_action(bot, players, selected_player, players_target, game_map, dt) # Gérer offensive si rien d'autre
                                )
                            )
                        )
                    )
                )
            )
        )
    )