import heapq
import math
from Controller.utils import get_snapped_angle, get_angle

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(game_map, position):
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

def find_nearest_walkable_tile(rounded_goal, game_map):
    open_set = [(0, rounded_goal)]
    visited = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if game_map.walkable_position(current):
            return current

        visited.add(current)
        for neighbor in get_neighbors(game_map, current):
            if neighbor not in visited:
                distance = heuristic(neighbor, rounded_goal)
                heapq.heappush(open_set, (distance, neighbor))

    return None

def walkable_goal(start, rounded_goal, game_map):
    entities = game_map.grid.get(rounded_goal, None)
    entity = list(entities)[0] if entities else None
    float_offset = None
    if entity:
        angle = get_angle((entity.x, entity.y), start)
        offset_x = ((entity.size - 1) / 2) * math.cos(math.radians(angle))
        offset_y = ((entity.size - 1) / 2) * math.sin(math.radians(angle))
        float_goal = (entity.x + offset_x, entity.y + offset_y)
        float_offset = float_goal
        rg = (round(float_goal[0]), round(float_goal[1]))
        if game_map.walkable_position(rg):
            return rg, float_offset
        tile = find_nearest_walkable_tile(rg, game_map)
        return tile, float_offset
    return rounded_goal, None

def a_star(start, float_goal, game_map):
    rounded_goal = (round(float_goal[0]), round(float_goal[1]))
    if not game_map.walkable_position(rounded_goal):
        rounded_goal, float_building_goal = walkable_goal(start, rounded_goal, game_map)
    else:
        float_building_goal = None

    if not rounded_goal or not game_map.walkable_position(rounded_goal):
        return []

    open_set = []
    rs = (round(start[0]), round(start[1]))
    heapq.heappush(open_set, (0, rs))
    came_from = {}
    g_score = {rs: 0}
    f_score = {rs: heuristic(rs, rounded_goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == rounded_goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            if float_building_goal and game_map.walkable_position((round(float_building_goal[0]), round(float_building_goal[1]))):
                path.append(float_building_goal)
            elif game_map.walkable_position(float_goal):
                path.append(float_goal)
            return path

        for neighbor in get_neighbors(game_map, current):
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, rounded_goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []

