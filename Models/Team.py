from Settings.setup import LEAN_NUMBER_OF_TOWER_CENTRE, LEAN_STARTING_FOOD, LEAN_STARTING_GOLD, LEAN_STARTING_VILLAGERS, LEAN_STARTING_WOOD
from Settings.setup import MEAN_NUMBER_OF_TOWER_CENTRE, MEAN_STARTING_FOOD, MEAN_STARTING_GOLD, MEAN_STARTING_VILLAGERS, MEAN_STARTING_WOOD
from Settings.setup import MARINES_NUMBER_OF_TOWER_CENTRE, MARINES_STARTING_FOOD, MARINES_STARTING_GOLD, MARINES_STARTING_VILLAGERS, MARINES_NUMBER_OF_ARCHERY_RANGES, MARINES_NUMBER_OF_BARRACKS, MARINES_NUMBER_OF_STABLES, MARINES_STARTING_WOOD
from Models.Building import TownCentre, Barracks, Stable, ArcheryRange
from Models.Unit import Villager
from Models.Resources import Resources
import webbrowser

class Team:
    def __init__(self, difficulty):
        self.resources = None
        self.units = []
        self.buildings = []
        
        if difficulty == 'lean':
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
        file=open("données.html","w")
        template="""
<html>
<head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
<title> Données du jeu </title>
</head>
<body>
<h1>Données du jeu </h1>
    <details>
            <summary>Armée</summary>

"""     
        for u in self.units:
            template+="""

<p>
<b>id</b>:%s 
<b>acronym</b>: %s 
<b>tache</b>: %s   
<b>hp</b>: %d 
<b>position</b>:(%d,%d) 
</p>\n        

            """ %(u.id,u.acronym,u.task,u.hp,u.x,u.y)

        for b in self.buildings:
            template+="""

            """
        template+="""
    </details>
</body>
</html>
"""
        file.write(template)
        file.close()
        webbrowser.open("données.html")
        
