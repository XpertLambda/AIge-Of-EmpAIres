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
def priorty1(bot, enemy_team, players_target, game_map, dt):
    debug_print("Defending against attack.")
    bot.priorty1(enemy_team, players_target, dt)

def priority_2(bot, enemy_teams, game_map):
    debug_print("Attacking the enemy.")
    bot.priority_2(enemy_teams, game_map)

def priority_6(bot):
    debug_print("Repairing critical buildings.")
    bot.priority_6()

def priorty_5(bot):
    debug_print("Maintaining military units.")
    bot.priorite_5()

def priorty7(bot):
    debug_print("Managing resource shortages.")
    bot.priorty7()

def check_building_needs(bot):
    debug_print("Checking building needs.")
    return bot.check_building_needs()

def build_structure(bot):
    debug_print("Building structures.")
    if bot.check_building_needs():
        bot.build_structure()

# Conditions (Using Logic from Bot.py)
def is_under_attack(bot, enemy_team):
    return bot.is_under_attack(enemy_team)

def gold_food_wood_low(bot):
    return bot.get_resource_shortage() is not None

def building_needs(bot):
    return bot.check_building_needs()

def army_below_threshold(bot):
    return bot.get_military_unit_count(bot.player_team) < 20

def damaged_buildings(bot):
    return len(bot.get_critical_points()) > 0

# Decision Tree
def create_decision_tree(bot, enemy_team, enemy_teams, game_map, dt):
    return DecisionNode(
        condition=lambda: is_under_attack(bot, enemy_team),
        true_branch=DecisionNode(
            action=lambda: priorty1(bot, enemy_team, None, game_map, dt)
        ),
        false_branch=DecisionNode(
            condition=lambda: gold_food_wood_low(bot),
            true_branch=DecisionNode(
                action=lambda: priorty7(bot)
            ),
            false_branch=DecisionNode(
                condition=lambda: building_needs(bot),
                true_branch=DecisionNode(
                    condition=lambda: army_below_threshold(bot), 
                    true_branch=DecisionNode(
                        action=lambda: priorty_5(bot)
                    ),
                    false_branch=DecisionNode(
                        action=lambda: build_structure(bot)
                    )
                ),
                false_branch=DecisionNode(
                    condition=lambda: damaged_buildings(bot),
                    true_branch=DecisionNode(
                        action=lambda: priority_6(bot)
                    ),
                    false_branch=DecisionNode(
                        action=lambda: priority_2(bot, enemy_teams, game_map)
                    )
                )
            )
        )
    )

# Example Usage
bot = Bot(player_team="player_team", game_map="game_map", clock="clock")
decision_tree = create_decision_tree(
    bot=bot,
    enemy_team="enemy_team",
    enemy_teams=["enemy_team_1", "enemy_team_2"],
    game_map="game_map",
    dt="dt"
)

decision_tree.evaluate()
