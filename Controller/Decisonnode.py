from Controller.terminal_display_debug import debug_print
class Decision:
    def __init__(self, bot):
        self.bot = bot

    def execute(self):
        debug_print("Decision.execute() called")
        # Priority 1: Defense
        for enemy_team in self.bot.game_map.players:
            if enemy_team.teamID != self.bot.player_team.teamID:
                if self.bot.is_under_attack(enemy_team):
                    debug_print(f"Executing Priority 1: Defending against {enemy_team.teamID}")
                    self.bot.defend_under_attack(enemy_team, None, None)
                    return

        # Priority 7: Resource Shortage
        resource_shortage = self.bot.get_resource_shortage()
        if resource_shortage:
            debug_print(f"Executing Priority 7: Reallocating villagers to {resource_shortage}")
            self.bot.reallocate_villagers(resource_shortage)
            return

        # Priority 4: Building Needs
        needed_buildings = self.bot.check_building_needs()
        if needed_buildings:
            debug_print(f"Executing Priority 4: Building {needed_buildings}")
            self.bot.build_structure(self.bot.clock)
            return
        
        # Priority 5: Train Units
        if len(self.bot.get_military_units()) < 20:
            debug_print("Executing Priority 5: Training military units")
            self.bot.balance_units()
            return

        # Priority 2: Attack
        debug_print("Executing Priority 2: Attacking")
        self.bot.maintain_army()
