# Search Algorithm Comparison

## Test setup

All three algorithms were run on each saved 24 × 24 map with four-direction movement, start `(1, 1)` and goal `(22, 22)`. Open walkway costs 1 per entered cell, gravel (`~`) costs 3, and walls (`#`) cannot be entered. The start cell itself is not charged.

**Metrics:** path steps count edges in the returned route; path cost sums terrain-entry costs; nodes expanded counts cells removed from the frontier and processed, including the goal when reached.

## Results

| Map | Algorithm | Path steps | Path cost | Nodes expanded | Outcome |
|---|---:|---:|---:|---:|---|
| Open campus | BFS | 42 | 42 | 521 | Route found |
| Open campus | Dijkstra | 42 | 42 | 521 | Route found |
| Open campus | A* | 42 | 42 | 415 | Route found |
| Winding campus | BFS | 44 | 48 | 468 | Route found |
| Winding campus | Dijkstra | 44 | 44 | 468 | Route found |
| Winding campus | A* | 44 | 44 | 276 | Route found |
| Blocked campus (no route) | BFS | — | — | 288 | No route |
| Blocked campus (no route) | Dijkstra | — | — | 288 | No route |
| Blocked campus (no route) | A* | — | — | 288 | No route |

## Interpretation

**BFS** is the simplest choice when every traversable move has the same cost and the objective is the fewest steps. It explores in layers and therefore finds a minimum-step route, but it ignores the extra cost of gravel. On these weighted maps, its returned path can have a higher movement cost than Dijkstra or A* even when it uses fewer steps.

**Dijkstra** is the correct uninformed choice when movement costs differ and the lowest total travel cost matters. It accounts for gravel cost 3 and guarantees an optimal-cost route with non-negative costs, but it may expand many cells because it has no estimate of the goal direction.

**A*** uses the same movement costs as Dijkstra but prioritises cells using `g(n) + h(n)`. Manhattan distance is admissible here: with four-direction movement, at least the Manhattan number of steps remains, and each entered cell costs at least 1. It therefore never overestimates the remaining cost. A* usually expands fewer nodes than Dijkstra when the heuristic guides it toward the goal, while retaining optimality for this map model.

**No-route map:** the third map has a complete wall row separating the start from the goal. All three algorithms correctly exhaust the reachable region and report that no route exists rather than crashing.

## Reproducibility

Run `python main.py`, load maps with keys `1`–`3`, and press `SPACE` to animate BFS, Dijkstra and A* sequentially on the same grid. The on-screen results show path steps, path cost and nodes expanded. The values above are computed by the included search implementations for the default endpoints.

## Limitations

This is a static, four-neighbour grid model. It does not model trolley turning radius, speed, dynamic obstacles, pedestrian traffic, or real campus coordinates. BFS optimizes steps rather than weighted cost by design.