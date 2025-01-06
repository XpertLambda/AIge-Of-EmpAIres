import heapq
import math

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(unit, game_map, position):
    directions = [
        (1, 0), (0, 1), (-1, 0), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    neighbors = []
    for dx, dy in directions:
        neighbor = (position[0] + dx, position[1] + dy)
        if unit.is_tile_walkable(game_map, neighbor[0], neighbor[1]):
            neighbors.append(neighbor)
    return neighbors

def find_nearest_walkable_tile(unit, goal, game_map):
    open_set = [(0, goal)]
    visited = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if unit.is_tile_walkable(game_map, current[0], current[1]):
            return current

        visited.add(current)
        for neighbor in get_neighbors(unit, game_map, current):
            if neighbor not in visited:
                distance = heuristic(neighbor, goal)
                heapq.heappush(open_set, (distance, neighbor))

    return None

def a_star(unit, goal, game_map):
    if not unit.is_tile_walkable(game_map, goal[0], goal[1]):
        goal = find_nearest_walkable_tile(unit, goal, game_map)
        if not goal:
            unit.path = None
            return

    open_set = []
    heapq.heappush(open_set, (0, (round(unit.x), round(unit.y))))
    came_from = {}
    g_score = {(round(unit.x), round(unit.y)): 0}
    f_score = {(round(unit.x), round(unit.y)): heuristic((round(unit.x), round(unit.y)), goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            unit.path = path
            return

        for neighbor in get_neighbors(unit, game_map, current):
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    unit.path = None
