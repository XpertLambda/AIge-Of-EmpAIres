import time

class Entity:
    HEALTH_BAR_DISPLAY_DURATION = 5  # Durée d'affichage de la barre de vie (en secondes)

    def __init__(self, x, y, team, acronym, size):
        self.x = x
        self.y = y
        self.team = team
        self.acronym = acronym
        self.size = size

        # Added for health bar
        self.last_damage_time = 0
        self.last_clicked_time = 0
        self.max_hp = None  # sera défini dans les sous-classes après hp

    def notify_damage(self):
        self.last_damage_time = time.time()

    def notify_clicked(self):
        self.last_clicked_time = time.time()

    def should_draw_health_bar(self):
        if not hasattr(self, 'hp') or self.hp <= 0 or self.max_hp is None or self.max_hp <= 0:
            return False
        current_time = time.time()
        return ((current_time - self.last_damage_time) < self.HEALTH_BAR_DISPLAY_DURATION) or \
               ((current_time - self.last_clicked_time) < self.HEALTH_BAR_DISPLAY_DURATION)

    def get_health_ratio(self):
        if not hasattr(self, 'hp') or self.max_hp is None or self.max_hp == 0:
            return 0
        return self.hp / self.max_hp
