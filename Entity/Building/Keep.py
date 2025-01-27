from collections import deque
from Entity.Building import Building
from Models.Resources import Resources
import math
from Projectile.Arrow import *

class Keep(Building):
    def __init__(self, team, x=0, y=0):
        self.attack_power = 5
        self.attack_range = 8
        self.attack_speed = 1.1
        self.attack_target = None
        self.attack_timer = 0

        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='K',
            size=1,
            max_hp=800,
            cost=Resources(food=0, gold=125, wood=35),
            buildTime=80,
            attack_power=self.attack_power,
            attack_range=self.attack_range
        )


    def update(self, game_map, dt):
        if self.isAlive():
            self.seekConstruction(dt)  
            self.seekAttack(game_map, dt)            
            self.seekIdle()
        else:
            self.death(game_map)
        self.animator(dt)

    def scanRange(self, game_map):
        if self.attack_target:
            return
        
        grid = game_map.grid
        max_x, max_y = game_map.num_tiles_x, game_map.num_tiles_y
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        
        visited = set([(self.x, self.y)])
        queue = deque([(self.x, self.y, 0)])  # (x, y, distance)
        
        while queue:
            cx, cy, dist = queue.popleft()
            
            if dist > self.attack_range:
                break
            
            if (cx, cy) in grid:
                for entity in grid[(cx, cy)]:
                    if entity.team is not None and entity.team != self.team:
                        self.attack_target = entity
                        return
            if dist < self.attack_range:
                for dx, dy in directions:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < max_x and 0 <= ny < max_y and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny, dist + 1))

    def seekAttack(self, game_map, dt):
        if self.isBuilt():
            self.scanRange(game_map)
            if not self.attack_target:
                return
            if self.attack_target.isAlive():
                if hasattr(self.attack_target, 'path'):
                    distance = math.dist((self.x, self.y), (self.attack_target.x, self.attack_target.y))
                    distance -= (self.attack_target.hitbox + self.attack_range)
                else:
                    corner_distance = self.attack_target.size / 2.0
                    left = self.attack_target.x - corner_distance
                    right = self.attack_target.x + corner_distance
                    top = self.attack_target.y - corner_distance
                    bottom = self.attack_target.y + corner_distance
                    closest_point = (
                        max(left, min(self.x, right)),
                        max(top, min(self.y, bottom))
                    )
                    distance = math.dist(closest_point, (self.x, self.y)) - self.attack_range          
                
                if distance <= 0 :
                    if self.attack_timer == 0:
                        arrow = Arrow(self, self.attack_target)
                        arrow.launch(game_map, z_launch=5.5)

                    self.state = 'attack'
                    self.attack_timer += dt
                    if self.attack_timer >= self.attack_speed:
                        self.attack_target.hp -= self.attack_power
                        self.attack_timer = 0
                else :
                    self.attack_timer = 0
            else: 
                self.attack_target = None
