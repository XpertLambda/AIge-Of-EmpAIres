import heapq
import math
from Controller.isometric_utils import get_snapped_angle, get_angle
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
        if game_map.walkable_position(neighbor):
            neighbors.append(neighbor)
    return neighbors

def find_nearest_walkable_tile(unit, goal, game_map):
    open_set = [(0, goal)]
    visited = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if game_map.walkable_position(current):
            return current

        visited.add(current)
        for neighbor in get_neighbors(unit, game_map, current):
            if neighbor not in visited:
                distance = heuristic(neighbor, goal)
                heapq.heappush(open_set, (distance, neighbor))

    return None

def walkable_goal(unit, goal, game_map):
    entities = game_map.grid.get(goal, None)
    entity = list(entities)[0] if entities else None
    if entity:
        angle = get_angle((entity.x, entity.y), (unit.x, unit.y))
        offset_x = ((entity.size - 1) / 2) * math.cos(math.radians(angle))
        offset_y = ((entity.size - 1) / 2) * math.sin(math.radians(angle))
        goal = (entity.x + offset_x , entity.y + offset_y)
        rounded_goal = (round(goal[0]), round(goal[1]))
        if game_map.walkable_position(rounded_goal):
            return rounded_goal
        return find_nearest_walkable_tile(unit, rounded_goal, game_map)
    return goal

def a_star(unit, goal, game_map):
    if not game_map.walkable_position(goal):
        goal = walkable_goal(unit, goal, game_map)
    if not goal or not game_map.walkable_position(goal):
        return []

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
            return path

        for neighbor in get_neighbors(unit, game_map, current):
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []

