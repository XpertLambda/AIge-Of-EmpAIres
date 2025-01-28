# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\Decisonnode.py
from Controller.Bot import *
from Controller.terminal_display_debug import debug_print

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

def are_buildings_needed_condition(bot):
    return bot.check_building_needs()

def is_army_below_threshold_condition(bot):
    return bot.get_military_unit_count(bot.player_team) < 15 # Reduced threshold for example

def are_damaged_buildings_condition(bot):
    return len(bot.get_critical_points()) > 0

def is_military_count_low_condition(bot):
    return bot.get_military_unit_count(bot.player_team) < 10 # Example threshold

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

# --- Decision Trees ---

def create_economic_decision_tree(bot, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target):
    """Decision tree for Economic mode - focuses on economy, defends if attacked."""
    return DecisionNode(
        condition=lambda: is_under_attack_condition(bot, enemy_team),
        true_branch=DecisionNode(
            action=lambda: defend_action(bot, enemy_team, players_target, game_map, dt) # Défend si attaqué
        ),
        false_branch=DecisionNode(
            condition=lambda: is_resource_shortage_condition(bot),
            true_branch=DecisionNode(
                action=lambda: address_resource_shortage_action(bot) # Fix resource shortage
            ),
            false_branch=DecisionNode(
                condition=lambda: are_buildings_needed_condition(bot),
                true_branch=DecisionNode(
                    action=lambda: build_needed_structure_action(bot) # Build economic buildings
                ),
                false_branch=DecisionNode( # If no urgent needs, balance army
                    action=lambda: balance_army_action(bot)
                )
            )
        )
    )

def create_defensive_decision_tree(bot, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target):
    """Decision tree for Defensive mode - focuses on defense and strong economy."""
    return DecisionNode(
        condition=lambda: is_under_attack_condition(bot, enemy_team),
        true_branch=DecisionNode(
            action=lambda: defend_action(bot, enemy_team, players_target, game_map, dt) # Prioritize defense
        ),
        false_branch=DecisionNode(
            condition=lambda: are_damaged_buildings_condition(bot),
            true_branch=DecisionNode(
                action=lambda: repair_buildings_action(bot) # Repair buildings if damaged
            ),
            false_branch=DecisionNode(
                condition=lambda: is_resource_shortage_condition(bot),
                true_branch=DecisionNode(
                    action=lambda: address_resource_shortage_action(bot) # Ensure good economy
                ),
                false_branch=DecisionNode( # If base is secure and economy good, then balance army
                    action=lambda: balance_army_action(bot)
                )
            )
        )
    )


def create_offensive_decision_tree(bot, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target):
    """Decision tree for Offensive mode - focuses on aggressive military actions."""
    return DecisionNode(
        condition=lambda: is_under_attack_condition(bot, enemy_team),
        true_branch=DecisionNode(
            action=lambda: defend_action(bot, enemy_team, players_target, game_map, dt) # Défend si attaqué en premier
        ),
        false_branch=DecisionNode(
            condition=lambda: is_army_below_threshold_condition(bot),
            true_branch=DecisionNode(
                action=lambda: balance_army_action(bot) # Build army if small
            ),
            false_branch=DecisionNode( # If army is decent size, attack!
                action=lambda: manage_offense_action(bot, players, selected_player, players_target, game_map, dt) # Manage offensive battle
            )
        )
    )

def create_default_decision_tree(bot, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target):
    """Fallback decision tree - a balanced approach."""
    return DecisionNode(
        condition=lambda: is_under_attack_condition(bot, enemy_team),
        true_branch=DecisionNode(
            action=lambda: defend_action(bot, enemy_team, players_target, game_map, dt)
        ),
        false_branch=DecisionNode(
            condition=lambda: is_resource_shortage_condition(bot),
            true_branch=DecisionNode(
                action=lambda: address_resource_shortage_action(bot)
            ),
            false_branch=DecisionNode(
                condition=lambda: are_buildings_needed_condition(bot),
                true_branch=DecisionNode(
                    action=lambda: build_needed_structure_action(bot)
                ),
                false_branch=DecisionNode(
                    condition=lambda: is_military_count_low_condition(bot),
                    true_branch=DecisionNode(
                        action=lambda: balance_army_action(bot)
                    ),
                    false_branch=DecisionNode(
                        action=lambda: manage_offense_action(bot, players, selected_player, players_target, game_map, dt) # Balanced approach: manage offense if nothing else needed
                    )
                )
            )
        )
    )