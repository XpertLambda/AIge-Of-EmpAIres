from Controller.Bot import *


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


# Priority Actions (Using Logic from Bot.py)
def priorty1(player_team, enemy_team, players_target, game_map, dt):
    debug_print("Defending against attack.")
    priorty1(player_team, enemy_team, players_target, game_map, dt)

def priority_2(player_team, enemy_teams, game_map):
    debug_print("Attacking the enemy.")
    priority_2(players,selected_player,players_target)

def priority_6(player_team):
    debug_print("Repairing critical buildings.")
    priority_6(player_team)

def priorty_5(player_team):
    debug_print("Maintaining military units.")
    priorite_5(player_team)

def priorty7(player_team, game_map, ):
    debug_print("Managing resource shortages.")
    resource_shortage = get_resource_shortage(player_team.resources, RESOURCE_THRESHOLDS=RESOURCE_THRESHOLDS)
    if resource_shortage:
        reallocate_villagers(resource_shortage, player_team, game_map)

def check_building_needs():
    debug_print("Checking building needs.")
    return check_building_needs()

def build_structure(player_team):
    debug_print("Building structures.")
    if check_building_needs():
        build_structure(player_team)


# Conditions (Using Logic from Bot.py)
def is_under_attack(player_team, enemy_team):
    return is_under_attack(player_team, enemy_team)

def gold_food_wood_low(player_team, s):
    return get_resource_shortage(player_team.resources,RESOURCE_THRESHOLDS=RESOURCE_THRESHOLDS ) is not None

def building_needs(player_team):
    return check_building_needs()

def army_below_threshold(player_team):
    return get_military_unit_count(player_team) < 20

def damaged_buildings(player_team):
    return len(get_damaged_buildings(player_team)) > 0





# Decision Tree
def create_decision_tree(player_team, enemy_team, enemy_teams, game_map, dt, resource_thresholds):
    return DecisionNode(
        condition=lambda: is_under_attack(player_team, enemy_team),
        true_branch=DecisionNode(
            action=lambda: priorty1(player_team, enemy_team, None, game_map, dt)
        ),
        false_branch=DecisionNode(
            condition=lambda: gold_food_wood_low(player_team, resource_thresholds),
            true_branch=DecisionNode(
                action=lambda: priorty7(player_team, game_map, resource_thresholds)
            ),
            false_branch=DecisionNode(
                condition=lambda: building_needs(player_team),
                true_branch=DecisionNode(
                    condition=lambda: army_below_threshold(player_team), 
                    true_branch=DecisionNode(
                        action=lambda: priorite_5(player_team)
                    ),
                    false_branch=DecisionNode(
                        action=lambda: build_structure(player_team)
                    )
                ),
                false_branch=DecisionNode(
                    condition=lambda: damaged_buildings(player_team),
                    true_branch=DecisionNode(
                        action=lambda: priority_6(player_team)
                    ),
                    false_branch=DecisionNode(
                        action=lambda: priority_2(player_team, enemy_teams, game_map)
                    )
                )
            )
        )
    )


# Example Usage
resource_thresholds = RESOURCE_THRESHOLDS
decision_tree = create_decision_tree(
    player_team="player_team",
    enemy_team="enemy_team",
    enemy_teams=["enemy_team_1", "enemy_team_2"],
    game_map="game_map",
    dt="dt",
    resource_thresholds=resource_thresholds
)

decision_tree.evaluate()
