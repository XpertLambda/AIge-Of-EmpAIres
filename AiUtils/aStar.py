import heapq
import math
from Controller.isometric_utils import get_snapped_angle
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

def adjust_goal_to_walkable(unit, goal, game_map):
    entities = game_map.grid.get(goal, None)
    entity = list(entities)[0] if entities else None
    if entity:
        center_x = entity.x + (entity.size - 1) / 2
        center_y = entity.y + (entity.size - 1) / 2
        snapped_angle = get_snapped_angle((center_x, center_y), (unit.x, unit.y))
        offset_distance = max(1, 2 / entity.size)  # Ensure a reasonable offset
        offset_x = center_x + math.cos(math.radians(snapped_angle)) * offset_distance
        offset_y = center_y + math.sin(math.radians(snapped_angle)) * offset_distance
        offset_goal = (round(offset_x), round(offset_y))
        if game_map.walkable_position(offset_goal):
            return offset_goal
        return find_nearest_walkable_tile(unit, offset_goal, game_map)
    return goal


def a_star(unit, goal, game_map):
    if not game_map.walkable_position(goal):
        goal = adjust_goal_to_walkable(unit, goal, game_map)
    if not goal or not game_map.walkable_position(goal):
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

    unit.path = []

