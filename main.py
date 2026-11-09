"""
Campus Delivery Search Visualiser
Run: python main.py
Controls:
  Click Set START / Set GOAL, then click a grid cell.
  Click BFS / DIJKSTRA / A* to animate one algorithm.
  Click RUN ALL to compare all three on the same map.
  Press 1, 2, 3 to load a map; SPACE runs all; R resets.
"""
import pygame
from pathlib import Path
from search import breadth_first_search, dijkstra_search, astar_search
from map_loader import load_map, MapFormatError

pygame.init()

CELL = 28
GRID_X, GRID_Y = 20, 72
PANEL_X = GRID_X + 24 * CELL + 28
WIDTH, HEIGHT = PANEL_X + 300, 820
FPS = 60

COLORS = {
    "background": (24, 29, 39),
    "panel": (34, 41, 54),
    "grid": (64, 73, 88),
    "open": (224, 231, 236),
    "wall": (54, 62, 73),
    "slow": (205, 157, 75),
    "start": (48, 180, 105),
    "goal": (220, 75, 75),
    "visited": (90, 155, 225),
    "path": (248, 218, 80),
    "text": (245, 247, 250),
    "muted": (174, 185, 198),
    "button": (66, 83, 108),
    "button_active": (55, 125, 150),
    "success": (100, 210, 145),
    "error": (245, 125, 115),
}

MAP_FILES = [
    ("Open campus", "maps/map1_open.csv"),
    ("Winding campus", "maps/map2_winding.csv"),
    ("Blocked campus", "maps/map3_blocked.csv"),
]
ALGORITHMS = {
    "BFS": breadth_first_search,
    "Dijkstra": dijkstra_search,
    "A*": astar_search,
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Campus Delivery — Search Algorithm Comparison")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 16)
small = pygame.font.SysFont("arial", 13)
heading = pygame.font.SysFont("arial", 22, bold=True)
big = pygame.font.SysFont("arial", 28, bold=True)

def label(surface, text, x, y, color=None, use_font=None):
    surface.blit((use_font or font).render(str(text), True, color or COLORS["text"]), (x, y))

def button(rect, text, active=False):
    pygame.draw.rect(screen, COLORS["button_active"] if active else COLORS["button"], rect, border_radius=7)
    pygame.draw.rect(screen, (105, 122, 145), rect, 1, border_radius=7)
    txt = small.render(text, True, COLORS["text"])
    screen.blit(txt, txt.get_rect(center=rect.center))

def cell_center(cell):
    r, c = cell
    return GRID_X + c * CELL + CELL // 2, GRID_Y + r * CELL + CELL // 2

def safe_load(index):
    name, rel = MAP_FILES[index]
    return load_map(Path(__file__).parent / rel)

map_index = 0
grid = safe_load(map_index)
rows, cols = len(grid), len(grid[0])
start, goal = (1, 1), (rows - 2, cols - 2)
# Keep endpoints on traversable cells.
if grid[start[0]][start[1]] == "#":
    grid[start[0]][start[1]] = "."
if grid[goal[0]][goal[1]] == "#":
    grid[goal[0]][goal[1]] = "."

mode = None
status = "Choose an algorithm or press SPACE to run all three."
current_name = None
current_result = None
visited_shown = []
path_shown = []
animation_index = 0
last_frame = 0
queue_all = []
results = {}
selecting = None
error_message = ""

def clear_animation():
    global current_name, current_result, visited_shown, path_shown, animation_index, queue_all
    current_name = None
    current_result = None
    visited_shown = []
    path_shown = []
    animation_index = 0
    queue_all = []

def set_map(index):
    global map_index, grid, rows, cols, start, goal, results, status, error_message
    clear_animation()
    map_index = index
    grid = safe_load(map_index)
    rows, cols = len(grid), len(grid[0])
    start, goal = (1, 1), (rows - 2, cols - 2)
    if grid[start[0]][start[1]] == "#":
        grid[start[0]][start[1]] = "."
    if grid[goal[0]][goal[1]] == "#":
        grid[goal[0]][goal[1]] = "."
    results = {}
    status = f"Loaded {MAP_FILES[index][0]}."
    error_message = ""

def begin_algorithm(name):
    global current_name, current_result, visited_shown, path_shown, animation_index, last_frame, status, error_message
    try:
        current_result = ALGORITHMS[name](grid, start, goal)
        current_name = name
        visited_shown = []
        path_shown = []
        animation_index = 0
        last_frame = pygame.time.get_ticks()
        results[name] = current_result
        status = f"Animating {name}..."
        error_message = ""
    except ValueError as exc:
        error_message = str(exc)
        status = "Could not run search."

def run_all():
    global queue_all
    queue_all = ["BFS", "Dijkstra", "A*"]
    results.clear()
    begin_algorithm(queue_all.pop(0))

def next_queued():
    if queue_all:
        begin_algorithm(queue_all.pop(0))

def draw():
    screen.fill(COLORS["background"])
    label(screen, "CAMPUS DELIVERY SEARCH VISUALISER", 20, 18, use_font=heading)
    label(screen, "Select start and goal cells, then compare the search strategies.", 20, 44, COLORS["muted"], small)

    # Map cells
    for r in range(rows):
        for c in range(cols):
            value = grid[r][c]
            color = COLORS["open"] if value == "." else COLORS["wall"] if value == "#" else COLORS["slow"]
            cell = (r, c)
            if cell in visited_shown:
                color = COLORS["visited"]
            if cell in path_shown:
                color = COLORS["path"]
            if cell == start:
                color = COLORS["start"]
            if cell == goal:
                color = COLORS["goal"]
            rect = pygame.Rect(GRID_X + c * CELL, GRID_Y + r * CELL, CELL, CELL)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, COLORS["grid"], rect, 1)

    label(screen, "MAP", GRID_X, 50, COLORS["muted"], small)
    # Side panel
    pygame.draw.rect(screen, COLORS["panel"], (PANEL_X, 14, 280, HEIGHT - 28), border_radius=12)
    label(screen, "MAPS", PANEL_X + 16, 30, use_font=heading)
    for i, (name, _) in enumerate(MAP_FILES):
        button(pygame.Rect(PANEL_X + 15, 65 + i * 38, 250, 30), f"{i+1}. {name}", map_index == i)

    label(screen, "SET POINTS", PANEL_X + 16, 190, use_font=heading)
    button(pygame.Rect(PANEL_X + 15, 225, 120, 34), "Set START", selecting == "start")
    button(pygame.Rect(PANEL_X + 145, 225, 120, 34), "Set GOAL", selecting == "goal")
    label(screen, f"Start: {start}", PANEL_X + 16, 270, COLORS["success"], small)
    label(screen, f"Goal:  {goal}", PANEL_X + 16, 290, COLORS["error"], small)

    label(screen, "RUN SEARCH", PANEL_X + 16, 330, use_font=heading)
    button(pygame.Rect(PANEL_X + 15, 365, 78, 34), "BFS")
    button(pygame.Rect(PANEL_X + 101, 365, 78, 34), "Dijkstra")
    button(pygame.Rect(PANEL_X + 187, 365, 78, 34), "A*")
    button(pygame.Rect(PANEL_X + 15, 407, 250, 38), "RUN ALL (SPACE)", True)
    button(pygame.Rect(PANEL_X + 15, 453, 250, 30), "Reset animation (R)")

    label(screen, "LEGEND", PANEL_X + 16, 505, use_font=heading)
    legend = [
        ("open walkway", COLORS["open"]),
        ("building / wall", COLORS["wall"]),
        ("slow ground (cost 3)", COLORS["slow"]),
        ("visited / expanded", COLORS["visited"]),
        ("final path", COLORS["path"]),
        ("start", COLORS["start"]),
        ("goal", COLORS["goal"]),
    ]
    for i, (txt, color) in enumerate(legend):
        y = 540 + i * 25
        pygame.draw.rect(screen, color, (PANEL_X + 17, y, 17, 17))
        pygame.draw.rect(screen, COLORS["grid"], (PANEL_X + 17, y, 17, 17), 1)
        label(screen, txt, PANEL_X + 44, y + 1, COLORS["text"], small)

    label(screen, "CURRENT RUN", PANEL_X + 16, 725, use_font=heading)
    label(screen, status[:38], PANEL_X + 16, 754, COLORS["muted"], small)
    if current_name and current_result:
        label(screen, f"{current_name}: {len(visited_shown)}/{len(current_result.visited)} visited", PANEL_X + 16, 775, COLORS["text"], small)

    # Results area below grid, if there is room.
    table_y = GRID_Y + rows * CELL + 12
    label(screen, "RESULTS — path steps | path cost | nodes expanded", 20, table_y, COLORS["muted"], small)
    for i, name in enumerate(("BFS", "Dijkstra", "A*")):
        res = results.get(name)
        if res:
            summary = f"{name}: " + (f"{res.path_steps} | {res.path_cost:g} | {res.expanded}" if res.found else "NO ROUTE")
            label(screen, summary, 20 + i * 260, table_y + 19, COLORS["text"], small)
    if error_message:
        label(screen, error_message, PANEL_X + 16, 795, COLORS["error"], small)

def choose_cell(pos):
    x, y = pos
    c = (x - GRID_X) // CELL
    r = (y - GRID_Y) // CELL
    if 0 <= r < rows and 0 <= c < cols:
        if grid[r][c] == "#":
            return None
        return (r, c)
    return None

running = True
while running:
    now = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                set_map(event.key - pygame.K_1)
            elif event.key == pygame.K_SPACE:
                run_all()
            elif event.key == pygame.K_r:
                clear_animation()
                results.clear()
                status = "Animation reset."
            elif event.key == pygame.K_b:
                begin_algorithm("BFS")
            elif event.key == pygame.K_d:
                begin_algorithm("Dijkstra")
            elif event.key == pygame.K_a:
                begin_algorithm("A*")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if PANEL_X + 15 <= pos[0] <= PANEL_X + 265:
                if 65 <= pos[1] < 95: set_map(0)
                elif 103 <= pos[1] < 133: set_map(1)
                elif 141 <= pos[1] < 171: set_map(2)
                elif 225 <= pos[1] < 259:
                    selecting = "start" if pos[0] < PANEL_X + 140 else "goal"
                    status = f"Click a walkable cell to set {selecting.upper()}."
                elif 365 <= pos[1] < 399:
                    if pos[0] < PANEL_X + 95: begin_algorithm("BFS")
                    elif pos[0] < PANEL_X + 180: begin_algorithm("Dijkstra")
                    else: begin_algorithm("A*")
                elif 407 <= pos[1] < 445:
                    run_all()
                elif 453 <= pos[1] < 483:
                    clear_animation()
                    results.clear()
                    status = "Animation reset."
            if selecting:
                cell = choose_cell(pos)
                if cell:
                    if selecting == "start": start = cell
                    else: goal = cell
                    clear_animation()
                    results.clear()
                    status = f"{selecting.upper()} set to {cell}."
                    selecting = None

    # Animate visited cells, then reveal final path.
    if current_result and current_name:
        if animation_index < len(current_result.visited) and now - last_frame >= 12:
            visited_shown.append(current_result.visited[animation_index])
            animation_index += 1
            last_frame = now
        elif animation_index >= len(current_result.visited):
            path_shown = list(current_result.path)
            if not current_result.found:
                status = f"{current_name}: no route exists."
            else:
                status = f"{current_name} finished. Cost {current_result.path_cost:g}; expanded {current_result.expanded}."
            if queue_all and animation_index >= len(current_result.visited):
                # Pause briefly before starting the next queued algorithm.
                if now - last_frame >= 650:
                    next_queued()
                    last_frame = now

    draw()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
