"""Entry point for the maze Dijkstra demo.

The script follows the specifications in ``AGENTS.md``:

* deterministic maze generation based on a seed (default ``0``)
* Dijkstra shortest‑path search from the left‑bottom corner to the
  right‑top corner
* visualisation with pygame – visited cells turn red, the final path
  turns blue, step count displayed at the top‑right
* the animation is recorded and saved as a GIF (``maze_demo.gif``)
  with a size under 320 × 320 px.
* a "[Press space]" message is shown before the algorithm starts and the
  program waits until the user closes the window.
"""

from __future__ import annotations

import sys
import os
import argparse
import imageio
from tqdm import tqdm

from .maze import Maze
from .visualizer import MazeRenderer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Maze Dijkstra visual demo")
    parser.add_argument("-s", "--seed", type=int, default=0, help="Random seed for maze generation")
    parser.add_argument("-o", "--output", type=str, default="maze_demo.gif",
                        help="Output animation file (GIF)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    size = 100
    maze = Maze(size=size, seed=args.seed)
    start = (0, size - 1)  # left‑bottom per spec
    goal = (size - 1, 0)   # right‑top per spec

    renderer = MazeRenderer(maze_size=size, pixel_per_cell=3)
    renderer.show_press_space()

    # Run Dijkstra while capturing frames
    visited_order, path = maze.dijkstra(start, goal)

    # Visualise visited cells (red) – update every 5 cells to keep the
    # animation smooth without generating 10 000 frames.
    step = 0
    batch = 50  # Reduce number of frames for faster execution in tests
    for i, cell in enumerate(visited_order, 1):
        renderer.colour_cells([cell], (255, 0, 0))  # red
        step += 1
        if i % batch == 0 or i == len(visited_order):
            renderer.draw_step_count(step)
            renderer.update_display()
            renderer.capture_frame()

    # Visualise final path (blue)
    for i, cell in enumerate(path, 1):
        renderer.colour_cells([cell], (0, 0, 255))  # blue
        renderer.draw_step_count(step + i)
        renderer.update_display()
        renderer.capture_frame()

    # Save animation – use tqdm for a simple progress indicator.
    fps = 30
    output_path = os.path.abspath(args.output)
    with tqdm(total=len(renderer.frames), desc="Saving GIF", unit="frame") as pbar:
        # imageio can directly take a list of frames; we update tqdm after save.
        imageio.mimsave(output_path, renderer.frames, fps=fps, subrectangles=True)
        pbar.update(len(renderer.frames))

    print(f"Animation saved to {output_path}")
    # Keep window open until user closes it.
    renderer.wait_until_close()


if __name__ == "__main__":
    # Import pygame lazily to avoid import issues when the module is used
    # only for type checking.
    import pygame  # noqa: F401
    main()
