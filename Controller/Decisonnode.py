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
def defend_under_attack(player_team, enemy_team, players_target, game_map, dt):
    print("Defending against attack.")
    defend_under_attack(player_team, enemy_team, players_target, game_map, dt)

def priority_2(player_team, enemy_teams, game_map):
    print("Attacking the enemy.")
    target_team = choose_target(enemy_teams, player_team)
    if target_team:
        launch_attack(player_team, target_team, game_map)

def repair_critical_buildings(player_team):
    print("Repairing critical buildings.")
    damaged_buildings = get_damaged_buildings(player_team)
    for building in damaged_buildings:
        if can_repair_building(player_team, {"wood": 50}):  # Example cost
            assign_villager_to_repair(player_team, building)

def maintain_army(player_team):
    print("Maintaining military units.")
    maintain_army(player_team)

def check_and_address_resources(player_team, game_map, resource_thresholds):
    print("Managing resource shortages.")
    resource_shortage = get_resource_shortage(player_team.resources, resource_thresholds)
    if resource_shortage:
        reallocate_villagers(resource_shortage, player_team, game_map)

def check_building_needs():
    print("Checking building needs.")
    return check_building_needs()

def build_structure(player_team):
    print("Building structures.")
    if check_building_needs():
        build_structure(player_team)


# Conditions (Using Logic from Bot.py)
def is_under_attack(player_team, enemy_team):
    return is_under_attack(player_team, enemy_team)

def gold_food_wood_low(player_team, resource_thresholds):
    return get_resource_shortage(player_team.resources, resource_thresholds) is not None

def building_needs(player_team):
    return check_building_needs()

def army_below_threshold(player_team):
    return get_military_unit_count(player_team) < 20

def damaged_buildings(player_team):
    return len(get_damaged_buildings(player_team)) > 0


# Helper Functions
def choose_target(enemy_teams, player_team):
    count_max = float("inf")
    target_team = None
    for enemy_team in enemy_teams:
        count = sum(1 for unit in enemy_team.units if not isinstance(unit, Villager))
        if count < count_max:
            count_max = count
            target_team = enemy_team
    return target_team

def launch_attack(player_team, target_team, game_map):
    for unit in player_team.units:
        if not isinstance(unit, Villager):
            search_for_target(unit, target_team)
            unit.seekAttack(game_map)


# Decision Tree
def create_decision_tree(player_team, enemy_team, enemy_teams, game_map, dt, resource_thresholds):
    return DecisionNode(
        condition=lambda: is_under_attack(player_team, enemy_team),
        true_branch=DecisionNode(
            action=lambda: defend_under_attack(player_team, enemy_team, None, game_map, dt)
        ),
        false_branch=DecisionNode(
            condition=lambda: gold_food_wood_low(player_team, resource_thresholds),
            true_branch=DecisionNode(
                action=lambda: check_and_address_resources(player_team, game_map, resource_thresholds)
            ),
            false_branch=DecisionNode(
                condition=lambda: building_needs(player_team),
                true_branch=DecisionNode(
                    condition=lambda: army_below_threshold(player_team),
                    true_branch=DecisionNode(
                        action=lambda: maintain_army(player_team)
                    ),
                    false_branch=DecisionNode(
                        action=lambda: build_structure(player_team)
                    )
                ),
                false_branch=DecisionNode(
                    condition=lambda: damaged_buildings(player_team),
                    true_branch=DecisionNode(
                        action=lambda: repair_critical_buildings(player_team)
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
