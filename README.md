# Campus Delivery Search Visualiser

A beginner-friendly desktop Python/Pygame application comparing Breadth-First Search (BFS), Dijkstra and A* on the same campus grid.

## Requirements

- Python 3.9+
- Pygame

Install and run:

```bash
python -m pip install pygame
python main.py
```

## Grid file format

Maps are CSV files. Every cell is one character:

- `.` = open walkway (entry cost 1)
- `#` = wall/building (blocked)
- `~` = slow ground such as gravel (entry cost 3)

Maps must be rectangular and at least 20 rows by 20 columns. The loader rejects unknown symbols, empty rows, uneven row lengths and undersized maps. Change a map in `maps/` without changing Python code.

## Controls

- `1`, `2`, `3`: load one of the three sample maps
- Click **Set START** or **Set GOAL**, then click a walkable grid cell
- `B`: run BFS; `D`: run Dijkstra; `A`: run A*
- `SPACE`: run all three sequentially on the same map
- `R`: clear animation and results
- `ESC`: quit

You can also use the on-screen buttons.

## What is measured?

- **Path steps**: number of moves (edges) in the returned path
- **Path cost**: sum of costs for cells entered after leaving the start
- **Nodes expanded**: number of cells removed from the frontier and processed

BFS is optimal in number of steps when every move has equal cost. It does not optimize the higher gravel cost. Dijkstra and A* optimize weighted path cost.

## A* heuristic

The chosen heuristic is Manhattan distance:

`h(n) = |row(n) - row(goal)| + |col(n) - col(goal)|`

With four-direction movement, at least one move is required for each unit of row/column difference. Since every traversable entered cell costs at least 1, Manhattan distance never overestimates the remaining weighted cost. It is admissible (and consistent).

## Project structure

```text
campus_delivery_comparison/
├── main.py
├── search.py
├── map_loader.py
├── comparison.md
├── maps/
│   ├── map1_open.csv
│   ├── map2_winding.csv
│   └── map3_blocked.csv
└── screenshots/
    ├── map1_bfs.png
    ├── map1_dijkstra.png
    └── map1_astar.png
```

## Notes

The sample screenshots are static result visualisations generated from the same search implementations. Run the application to see the live cell-by-cell animation. Search results depend on the chosen start and goal.
