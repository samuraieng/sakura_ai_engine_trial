"""Maze generation and Dijkstra shortest path implementation.

The maze is a 100x100 grid. Walls are represented implicitly by the
adjacency list: a cell can move to a neighbor only if there is no wall
between them. The generation algorithm is a randomized depth‑first
search (recursive backtracker) which, when seeded with a fixed ``seed``
value, always produces the same maze.

Both the generation and the path‑finding expose information that the
visualiser can use:

* ``neighbors`` – a dictionary mapping a ``(x, y)`` cell tuple to a list
  of reachable neighbor tuples.
* ``dijkstra`` – returns the order in which cells were visited (for the
  red colouring) and the final path from ``start`` to ``goal`` (for the
  blue colouring).
"""

from __future__ import annotations

import random
import heapq
from typing import Dict, List, Tuple, Set

Cell = Tuple[int, int]


class Maze:
    """Represent a square maze.

    Attributes
    ----------
    size: int
        Number of cells per side (the maze is ``size`` × ``size``).
    seed: int
        Random seed used for deterministic generation.
    neighbors: Dict[Cell, List[Cell]]
        Adjacency list – for each cell a list of reachable neighbour
        cells (i.e., no wall between them).
    """

    def __init__(self, size: int = 100, seed: int = 0) -> None:
        self.size = size
        self.seed = seed
        self.neighbors: Dict[Cell, List[Cell]] = { (x, y): []
                                                   for y in range(size)
                                                   for x in range(size) }
        self._generate_maze()

    # ---------------------------------------------------------------------
    # Maze generation (recursive backtracker)
    # ---------------------------------------------------------------------
    def _generate_maze(self) -> None:
        random.seed(self.seed)
        visited: Set[Cell] = set()
        stack: List[Cell] = []

        start: Cell = (0, self.size - 1)  # left‑bottom as required
        visited.add(start)
        stack.append(start)

        while stack:
            current = stack[-1]
            x, y = current
            # Determine unvisited neighbours (4‑directional)
            candidates: List[Cell] = []
            if x > 0 and (x - 1, y) not in visited:
                candidates.append((x - 1, y))
            if x < self.size - 1 and (x + 1, y) not in visited:
                candidates.append((x + 1, y))
            if y > 0 and (x, y - 1) not in visited:
                candidates.append((x, y - 1))
            if y < self.size - 1 and (x, y + 1) not in visited:
                candidates.append((x, y + 1))

            if candidates:
                # Choose a random neighbour and carve a passage
                nxt = random.choice(candidates)
                self.neighbors[current].append(nxt)
                self.neighbors[nxt].append(current)
                visited.add(nxt)
                stack.append(nxt)
            else:
                stack.pop()

    # ---------------------------------------------------------------------
    # Dijkstra algorithm – returns visited order and the shortest path
    # ---------------------------------------------------------------------
    def dijkstra(self, start: Cell, goal: Cell) -> Tuple[List[Cell], List[Cell]]:
        """Run Dijkstra's algorithm.

        Parameters
        ----------
        start, goal: Cell
            Coordinates of the start and goal cells.

        Returns
        -------
        visited_order: List[Cell]
            Cells in the order they were extracted from the priority queue
            (used for the red colour in the visualiser).
        path: List[Cell]
            The shortest path from ``start`` to ``goal`` inclusive.
        """
        frontier: List[Tuple[int, Cell]] = []
        heapq.heappush(frontier, (0, start))
        came_from: Dict[Cell, Cell] = {start: start}
        cost_so_far: Dict[Cell, int] = {start: 0}
        visited_order: List[Cell] = []

        while frontier:
            current_cost, current = heapq.heappop(frontier)
            visited_order.append(current)
            if current == goal:
                break
            for nxt in self.neighbors[current]:
                new_cost = current_cost + 1  # uniform weight
                if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                    cost_so_far[nxt] = new_cost
                    priority = new_cost
                    heapq.heappush(frontier, (priority, nxt))
                    came_from[nxt] = current

        # Reconstruct path
        path: List[Cell] = []
        if goal in came_from:
            cur = goal
            while cur != start:
                path.append(cur)
                cur = came_from[cur]
            path.append(start)
            path.reverse()
        return visited_order, path
