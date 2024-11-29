from Settings.setup import LEAN_NUMBER_OF_TOWER_CENTRE, LEAN_STARTING_FOOD, LEAN_STARTING_GOLD, LEAN_STARTING_VILLAGERS, LEAN_STARTING_WOOD
from Settings.setup import MEAN_NUMBER_OF_TOWER_CENTRE, MEAN_STARTING_FOOD, MEAN_STARTING_GOLD, MEAN_STARTING_VILLAGERS, MEAN_STARTING_WOOD
from Settings.setup import MARINES_NUMBER_OF_TOWER_CENTRE, MARINES_STARTING_FOOD, MARINES_STARTING_GOLD, MARINES_STARTING_VILLAGERS, MARINES_NUMBER_OF_ARCHERY_RANGES, MARINES_NUMBER_OF_BARRACKS, MARINES_NUMBER_OF_STABLES, MARINES_STARTING_WOOD
from Models.Building import TownCentre, Barracks, Stable, ArcheryRange, Keep, Camp, House
from Models.Unit import Villager
from Models.Unit import Unit
from Models.Resources import Resources
import webbrowser

class Team:
    def __init__(self, difficulty):
        self.resources = Resources(0,0,0)
        self.units = []
        self.army=[]
        self.villagers=[]
        self.buildings = []
        
        if difficulty == 'lean':
            self.resources = {'food': LEAN_STARTING_FOOD, 'wood': LEAN_STARTING_WOOD, 'gold': LEAN_STARTING_GOLD}
            self.units = {'villagers': LEAN_STARTING_VILLAGERS}
            #self.buildings = {'town_centres': LEAN_NUMBER_OF_TOWER_CENTRE}
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
                self.army=set()

        elif difficulty == 'marines':
            self.resources = Resources(MARINES_STARTING_FOOD, MARINES_STARTING_WOOD, MARINES_STARTING_GOLD)
            
            # Ajout des bâtiments
                
            for _ in range(MARINES_NUMBER_OF_BARRACKS):
                self.buildings.append(Barracks())

            for _ in range(MARINES_NUMBER_OF_STABLES):
                self.buildings.append(Stable())

            for _ in range(MARINES_NUMBER_OF_ARCHERY_RANGES):
                self.buildings.append(ArcheryRange())
                
    def gestion_units(self):
        for u in self.units:
            if u.hp==0:
                units.remove(u)


    def builds(self,priority,acronym):
        #construit un batiment avec au moins un villageois + ceux disponible 
        #ou tout les villageois si priority
        #renvoie vrai si le batiment à était construit 
        #faux si manque de resources
        reussi=False
        i=1
        l=[]
        self.villagers[0].task="builds" 
        l.append(self.villagers[0])
        while i<len(self.villagers) and i<5:
            while(i<len(self.villagers) and (self.villagers[i].task!="nothing" or priority==False)):
                print(i)
                i+=1
            if(i<len(self.villagers)):
                self.villagers[i].task="builds" 
                l.append[self.villagers[i]]
        #time.sleep(build_time()) 
        for v in l:
            v.task="nothing"
        if(acronym=="B"):
            print("b")
            b=Barracks()
            if self.resources.wood>=b.woodCost:
                time.sleep(Barracks.build_time())
                self.buildings.append(b)

                self.resources.wood-=Barracks.woodCost
                reussi=True
        if(acronym=="A"):   
            a=ArcheryRange()
            if self.resources.wood>=a.woodCost:
                self.resources.wood-=a.woodCost
                self.buildings.append(a)
                reussi=True
        if(acronym=="S"):   
            s=Stable()
            if self.resources.wood>=s.woodCost:
                self.resources.wood-=s.woodCost
                self.buildings.append(s)
                reussi=True
        if(acronym=="C"):   
            c=Camp()
            if self.resources.wood>=c.woodCost:
                self.resources.wood-=c.woodCost
                self.buildings.append(c)
                reussi=True
        if(acronym=="K"):
            k=Keep()
            if self.resources.wood>=k.woodCost and self.resources.gold>=k.goldCost:
                self.resources.wood-=k.woodCost
                self.resources.gold-=k.goldCost
                self.buildings.append(k)
                reussi=True
        if(acronym=="F"):
            f=Farm()
            if self.resources.wood>=f.woodCost and self.resources.gold>=f.goldCost:
                self.resources.wood-=f.woodCost
                self.resources.gold-=f.goldCost
                self.buildings.append(f)
                reussi=True

        return reussi

    def battle(self,t):
        threads=[]
        print(len(self.army)-1)
        for i in range(0,len(t.army)):
            s=t.army[i]
            threads.append(threading.Thread(target=s.search, args=(t,self,map)))
        
        for i in range(0,len(self.army)):
    
            s=self.army[i]
            threads.append(threading.Thread(target=s.search,args=(self,t,map)))
        print("l",len(threads))
        for i in range(0,len(threads)):
            threads[i].start()
        for i in range(0,len(threads)):
         threads[i].join()
       

   


    def write_html(self):
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
        for u in self.army:
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
        with open("données.html", "w") as file:
            file.write(template)