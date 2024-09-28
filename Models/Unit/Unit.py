from Models.Team import Team

class Unit(Team):
    def __init__(self, acronym, cost_food, cost_gold, cost_wood, hp, attack, speed, training_time):
        self.acronym = acronym          # Nom de l'unité (Villager, Swordsman, etc.)
        self.cost_food = cost_food  # Coût en nourriture
        self.cost_gold = cost_gold  # Coût en or
        self.cost_wood = cost_wood  # Coût en bois
        self.hp = hp              # Points de vie
        self.attack = attack      # Attaque
        self.speed = speed        # Vitesse (en tuiles/seconde)
        self.training_time = training_time  # Temps d'entraînement (en secondes)