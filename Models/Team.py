# Models/Team.py

from Settings.setup import (
    LEAN_NUMBER_OF_TOWER_CENTRE, LEAN_STARTING_FOOD, LEAN_STARTING_GOLD, LEAN_STARTING_VILLAGERS, LEAN_STARTING_WOOD,
    MEAN_NUMBER_OF_TOWER_CENTRE, MEAN_STARTING_FOOD, MEAN_STARTING_GOLD, MEAN_STARTING_VILLAGERS, MEAN_STARTING_WOOD,
    MARINES_NUMBER_OF_TOWER_CENTRE, MARINES_STARTING_FOOD, MARINES_STARTING_GOLD, MARINES_STARTING_VILLAGERS,
    MARINES_NUMBER_OF_ARCHERY_RANGES, MARINES_NUMBER_OF_BARRACKS, MARINES_NUMBER_OF_STABLES, MARINES_STARTING_WOOD
)
from Models.Building import TownCentre, Barracks, Stable, ArcheryRange, Keep, Camp, House
from Models.Unit import Villager, Swordsman, Archer
from Models.Resources import Resources

class Team:
    def __init__(self, difficulty, nb):
        self.resources = None
        self.units = []     
        self.buildings = []
        self.nb = nb
        
        if difficulty == 'DEBUG':
            self.resources = Resources(LEAN_STARTING_FOOD, LEAN_STARTING_WOOD, LEAN_STARTING_GOLD)
        
            for _ in range(90):
                self.units.append(Swordsman())           
                self.units.append(Villager())           
                self.units.append(Archer())           
            for _ in range(1):
                self.buildings.append(TownCentre())
                self.buildings.append(ArcheryRange())
                self.buildings.append(Stable())
                self.buildings.append(Barracks())
                self.buildings.append(Keep())
                self.buildings.append(Camp())
                self.buildings.append(House())

        elif difficulty == 'lean':
            self.resources = Resources(LEAN_STARTING_FOOD, LEAN_STARTING_WOOD, LEAN_STARTING_GOLD)
        
            for _ in range(LEAN_STARTING_VILLAGERS):
                self.units.append(Villager())           
            for _ in range(LEAN_NUMBER_OF_TOWER_CENTRE):
                self.buildings.append(TownCentre())  

        elif difficulty == 'mean':
            self.resources = Resources(MEAN_STARTING_FOOD, MEAN_STARTING_WOOD, MEAN_STARTING_GOLD)
            for _ in range(MEAN_STARTING_VILLAGERS):
                self.units.append(Villager())
            for _ in range(MEAN_NUMBER_OF_TOWER_CENTRE):
                self.buildings.append(TownCentre())
                self.army = set()

        elif difficulty == 'marines':
            self.resources = Resources(MARINES_STARTING_FOOD, MARINES_STARTING_WOOD, MARINES_STARTING_GOLD)
            
            # Ajout des bâtiments
            for _ in range(MARINES_NUMBER_OF_BARRACKS):
                self.buildings.append(Barracks())

            for _ in range(MARINES_NUMBER_OF_STABLES):
                self.buildings.append(Stable())

            for _ in range(MARINES_NUMBER_OF_ARCHERY_RANGES):
                self.buildings.append(ArcheryRange())
            for _ in range(MARINES_STARTING_VILLAGERS):
                self.units.append(Villager())

    def write_html(self):
        template = """
<html>
<head>
    <meta charset="UTF-8">
    <title>Données du jeu</title>
</head>
<body>
<h1>Données du jeu</h1>
<details>
    <summary>Armée</summary>
"""     
        for u in self.army:
            template += """
<p>
<b>id</b>: {id} 
<b>acronym</b>: {acronym} 
<b>tâche</b>: {task}   
<b>hp</b>: {hp} 
<b>position</b>: ({x}, {y}) 
</p>
            """.format(id=u.id, acronym=u.acronym, task=u.task, hp=u.hp, x=u.x, y=u.y)
        for b in self.buildings:
            template += """
<p>
<b>Bâtiment</b>: {name} 
<b>Position</b>: ({x}, {y}) 
</p>
            """.format(name=type(b).__name__, x=b.x, y=b.y)
        template += """
</details>
</body>
</html>
"""
        with open("donnees.html", "w") as file:
            file.write(template)
