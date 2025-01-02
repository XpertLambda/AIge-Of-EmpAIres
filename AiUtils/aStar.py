# Chemin de /home/cyril/Documents/INSA/Projet_python/AiUtils/aStar.py
import heapq
import math

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def get_neighbors(unit, game_map, pos):
    directions= [(1,0),(0,1),(-1,0),(0,-1),
                 (1,1),(1,-1),(-1,1),(-1,-1)]
    for dx, dy in directions:
        nx, ny= pos[0]+ dx, pos[1]+ dy
        if unit.is_tile_walkable(game_map, nx, ny):
            yield (nx, ny)

def a_star(unit, goal, game_map):
    """
    If found => unit.path is list of tile coords (excl current).
    If none => unit.path=None
    """
    start= (round(unit.x), round(unit.y))
    if start== goal:
        unit.path=[]
        return

    open_set=[]
    heapq.heappush(open_set, (0, start))
    came_from={}
    g_score= {start:0}
    f_score= {start: heuristic(start, goal)}
    visited= set()

    while open_set:
        _, current= heapq.heappop(open_set)
        if current== goal:
            # reconstruct
            path=[]
            while current in came_from:
                path.append(current)
                current= came_from[current]
            path.reverse()
            if path and path[0]== start:
                path= path[1:]
            unit.path= path
            return

        if current in visited:
            continue
        visited.add(current)

        for neighbor in get_neighbors(unit, game_map, current):
            newg= g_score[current]+ 1
            if neighbor not in g_score or newg< g_score[neighbor]:
                came_from[neighbor]= current
                g_score[neighbor]= newg
                f_score[neighbor]= newg+ heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    unit.path= None
