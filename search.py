"""Classical graph-search implementations for the campus grid."""
from dataclasses import dataclass
from heapq import heappush, heappop
from collections import deque
from itertools import count

WALK_COST = 1
SLOW_COST = 3
DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))

@dataclass
class SearchResult:
    found: bool
    path: list
    visited: list
    path_cost: float
    expanded: int

    @property
    def path_steps(self):
        return max(0, len(self.path) - 1)

def validate_endpoints(grid, start, goal):
    if not grid or not grid[0]:
        raise ValueError("Grid is empty.")
    rows, cols = len(grid), len(grid[0])
    for point, name in ((start, "start"), (goal, "goal")):
        r, c = point
        if not (0 <= r < rows and 0 <= c < cols):
            raise ValueError(f"{name} cell {point} is outside the map.")
        if grid[r][c] == "#":
            raise ValueError(f"{name} cell {point} is a wall.")

def neighbors(grid, cell):
    rows, cols = len(grid), len(grid[0])
    r, c = cell
    for dr, dc in DIRECTIONS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#":
            yield (nr, nc)

def entry_cost(grid, cell):
    return SLOW_COST if grid[cell[0]][cell[1]] == "~" else WALK_COST

def reconstruct(came_from, start, goal):
    if goal not in came_from and goal != start:
        return []
    path = [goal]
    while path[-1] != start:
        path.append(came_from[path[-1]])
    path.reverse()
    return path

def path_cost(grid, path):
    # The starting cell is not charged; each entered cell incurs its terrain cost.
    return sum(entry_cost(grid, cell) for cell in path[1:])

def breadth_first_search(grid, start, goal):
    """BFS minimizes number of moves, not weighted terrain cost."""
    validate_endpoints(grid, start, goal)
    queue = deque([start])
    came_from = {start: None}
    visited = []
    while queue:
        current = queue.popleft()
        visited.append(current)
        if current == goal:
            path = reconstruct(came_from, start, goal)
            return SearchResult(True, path, visited, path_cost(grid, path), len(visited))
        for nxt in neighbors(grid, current):
            if nxt not in came_from:
                came_from[nxt] = current
                queue.append(nxt)
    return SearchResult(False, [], visited, float("inf"), len(visited))

def dijkstra_search(grid, start, goal):
    """Dijkstra minimizes the sum of entered-cell movement costs."""
    validate_endpoints(grid, start, goal)
    serial = count()
    frontier = [(0, next(serial), start)]
    distances = {start: 0}
    came_from = {}
    visited = []
    closed = set()
    while frontier:
        cost, _, current = heappop(frontier)
        if current in closed:
            continue
        closed.add(current)
        visited.append(current)
        if current == goal:
            path = reconstruct(came_from, start, goal)
            return SearchResult(True, path, visited, cost, len(visited))
        for nxt in neighbors(grid, current):
            new_cost = cost + entry_cost(grid, nxt)
            if new_cost < distances.get(nxt, float("inf")):
                distances[nxt] = new_cost
                came_from[nxt] = current
                heappush(frontier, (new_cost, next(serial), nxt))
    return SearchResult(False, [], visited, float("inf"), len(visited))

def astar_search(grid, start, goal):
    """
    A* minimizes weighted movement cost using Manhattan distance.
    Each move changes one coordinate by one, and every entered cell costs
    at least 1. Therefore Manhattan distance is a lower bound on remaining
    cost (admissible) and is consistent for these four-direction moves.
    """
    validate_endpoints(grid, start, goal)
    def heuristic(cell):
        return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])
    serial = count()
    frontier = [(heuristic(start), 0, next(serial), start)]
    distances = {start: 0}
    came_from = {}
    visited = []
    closed = set()
    while frontier:
        _, cost, _, current = heappop(frontier)
        if current in closed:
            continue
        closed.add(current)
        visited.append(current)
        if current == goal:
            path = reconstruct(came_from, start, goal)
            return SearchResult(True, path, visited, cost, len(visited))
        for nxt in neighbors(grid, current):
            new_cost = cost + entry_cost(grid, nxt)
            if new_cost < distances.get(nxt, float("inf")):
                distances[nxt] = new_cost
                came_from[nxt] = current
                heappush(frontier, (new_cost + heuristic(nxt), new_cost, next(serial), nxt))
    return SearchResult(False, [], visited, float("inf"), len(visited))
