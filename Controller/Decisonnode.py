# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\Decisonnode.py

class DecisionNode:
    def __init__(self, condition=None, true_branch=None, false_branch=None, action=None):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch
        self.action = action

    def evaluate(self):
        if self.condition and self.condition():
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
def is_under_attack_condition(bot):
    return bot.is_under_attack()

def is_resource_shortage_condition(bot):
    return bot.get_resource_shortage() 

def are_buildings_needed_condition(bot):
    return bot.check_building_needs()

def is_army_below_threshold_condition(bot):
    return bot.get_military_unit_count(bot.team) < 15 # Reduced threshold for example

def are_damaged_buildings_condition(bot):
    return len(bot.get_critical_points()) > 0

def is_military_count_low_condition(bot):
    return bot.get_military_unit_count(bot.team) < 10 # Example threshold

def should_expand_condition(bot):
    """Vérifie si le bot devrait s'étendre"""
    return bot.is_ready_to_expand()

# --- Actions ---
def defend_action(bot):
    print(f"Team {bot.team.teamID}: Decision Node Action: Defend under attack.")
    return bot.priorty1() # Using priority 1 for defense

def address_resource_shortage_action(bot):
    print(f"Team {bot.team.teamID}: Decision Node Action: Addressing resource shortage.")
    return bot.priority7() # Using priority 7 for resource management

def build_needed_structure_action(bot):
    print(f"Team {bot.team.teamID}: Decision Node Action: Building needed structures.")
    return bot.build_structure() # Build structure action

def balance_army_action(bot):
    print(f"Team {bot.team.teamID}: Decision Node Action: Balancing army units.")
    return bot.balance_units() # Balance units action

def repair_buildings_action(bot):
    print(f"Team {bot.team.teamID}: Decision Node Action: Repairing damaged buildings.")
    # Assuming priority_6 is for repair as per your initial request
    # if priority_6 action is not defined in Bot.py please check and adapt or replace with relevant repair logic
    return True # bot.priority_6() # Repair buildings action - adapt if needed

def manage_offense_action(bot):
    """Version simplifiée de manage_offense pour l'arbre de décision économique"""
    # On cible simplement le premier ennemi trouvé
    if bot.enemies:
        enemy_team = bot.enemies[0]
        military_units = bot.get_military_units()
        for unit in military_units:
            if not unit.attack_target or not unit.attack_target.isAlive():
                bot.search_for_target(unit, enemy_team, True)
    return True

def expansion_action(bot):
    """Action d'expansion"""
    return bot.manage_expansion()

# --- Decision Trees ---

def create_economic_decision_tree(bot):
    """Decision tree for Economic mode - now includes expansion"""
    print("Creating economic decision tree")
    return DecisionNode(
        condition = lambda: is_under_attack_condition(bot),
        true_branch = DecisionNode(
            action = lambda: defend_action(bot)
        ),
        false_branch = DecisionNode(
            condition = lambda: is_resource_shortage_condition(bot),
            true_branch = DecisionNode(
                action = lambda: address_resource_shortage_action(bot)
            ),
            false_branch = DecisionNode(
                condition = lambda: are_buildings_needed_condition(bot),
                true_branch = DecisionNode(
                    action = lambda: build_needed_structure_action(bot)
                ),
                false_branch = DecisionNode(
                    condition = lambda: should_expand_condition(bot),
                    true_branch = DecisionNode(
                        action = lambda: expansion_action(bot)
                    ),
                    false_branch = DecisionNode(
                        action = lambda: balance_army_action(bot)
                    )
                )
            )
        )
    )

def create_defensive_decision_tree(bot):
    """Decision tree for Defensive mode - focuses on defense and strong economy."""
    print("Creating defensive decision tree")
    return DecisionNode(
        condition=lambda: is_under_attack_condition(bot),
        true_branch=DecisionNode(
            action=lambda: defend_action(bot) # Prioritize defense
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

def create_offensive_decision_tree(bot):
    """Decision tree for Offensive mode - focuses on aggressive military actions."""
    print("Creating offensive decision tree")
    return DecisionNode(
        condition=lambda: is_under_attack_condition(bot),
        true_branch=DecisionNode(
            action=lambda: defend_action(bot) # Défend si attaqué en premier
        ),
        false_branch=DecisionNode(
            condition=lambda: is_army_below_threshold_condition(bot),
            true_branch=DecisionNode(
                action=lambda: balance_army_action(bot) # Build army if small
            ),
            false_branch=DecisionNode( # If army is decent size, attack!
                action=lambda: manage_offense_action(bot) # Manage offensive battle
            )
        )
    )

def create_default_decision_tree(bot):
    """Fallback decision tree - a balanced approach."""
    return DecisionNode(
        condition=lambda: is_under_attack_condition(bot),
        true_branch=DecisionNode(
            action=lambda: defend_action(bot)
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
                        action=lambda: manage_offense_action(bot) # Balanced approach: manage offense if nothing else needed
                    )
                )
            )
        )
    )