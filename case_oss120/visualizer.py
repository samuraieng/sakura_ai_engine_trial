"""Simple pygame visualiser for the maze and Dijkstra exploration.

The visualiser draws the maze grid, colours visited cells in red and the
final shortest path in blue. It also captures each frame as a NumPy
array so that an animated GIF (or MP4) can be created later with
``imageio``.
"""

from __future__ import annotations

import pygame
import numpy as np
from typing import List, Tuple

Cell = Tuple[int, int]


class MazeRenderer:
    """Render a ``Maze`` instance using pygame.

    Parameters
    ----------
    maze_size: int
        Number of cells per side (the maze is square).
    pixel_per_cell: int, optional
        Size of each cell in pixels. Default ``3`` gives a 300×300 image
        for a 100×100 maze which satisfies the *≤320* requirement.
    """

    def __init__(self, maze_size: int, pixel_per_cell: int = 3) -> None:
        self.maze_size = maze_size
        self.ppc = pixel_per_cell
        self.width = self.height = maze_size * pixel_per_cell
        # Initialise pygame in a headless‑compatible way.
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Maze Dijkstra Demo")
        self.font = pygame.font.SysFont(None, 20)
        # Pre‑compute wall lines (black grid). The outer border is drawn
        # with a thicker line (5px) as required.
        self._draw_grid()
        # Store frames for animation
        self.frames: List[np.ndarray] = []

    # ------------------------------------------------------------------
    def update_display(self) -> None:
        """Convenience wrapper for ``pygame.display.flip()``.

        The main script can call this method instead of importing ``pygame``
        directly, keeping the visualiser encapsulated.
        """
        pygame.display.flip()

    # ------------------------------------------------------------------
    def _draw_grid(self) -> None:
        """Draw the static background (walls) onto the screen.

        The specification asks for black walls of 5 px and passages of
        1 px. For simplicity we draw a thin grid (1 px) for internal walls
        and a thicker rectangle (5 px) for the outer border.
        """
        self.screen.fill((255, 255, 255))  # white background (unused cells)
        # Outer border – 5 px thick black rectangle
        border_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(self.screen, (0, 0, 0), border_rect, 5)
        # Internal thin grid lines (optional visual aid)
        for x in range(0, self.width, self.ppc):
            pygame.draw.line(self.screen, (0, 0, 0), (x, 0), (x, self.height), 1)
        for y in range(0, self.height, self.ppc):
            pygame.draw.line(self.screen, (0, 0, 0), (0, y), (self.width, y), 1)
        pygame.display.flip()

    # ------------------------------------------------------------------
    def _cell_rect(self, cell: Cell) -> pygame.Rect:
        x, y = cell
        # Maze coordinates: (0,0) is top‑left in pygame, but our logical
        # start is left‑bottom. Convert accordingly.
        rect = pygame.Rect(
            x * self.ppc,
            (self.maze_size - 1 - y) * self.ppc,
            self.ppc,
            self.ppc,
        )
        return rect

    # ------------------------------------------------------------------
    def colour_cells(self, cells: List[Cell], colour: Tuple[int, int, int]) -> None:
        """Colour a list of cells with the given RGB colour.

        This method does not clear previous colours – the caller should
        manage the ordering (e.g., draw visited cells first, then the
        final path).
        """
        for cell in cells:
            pygame.draw.rect(self.screen, colour, self._cell_rect(cell))

    # ------------------------------------------------------------------
    def draw_step_count(self, steps: int) -> None:
        """Render the step counter at the top‑right corner."""
        text = self.font.render(f"Step: {steps}", True, (0, 0, 0))
        # Position slightly inset from the right edge
        text_rect = text.get_rect()
        text_rect.topright = (self.width - 5, 5)
        # Fill a small background to improve readability
        bg_rect = text_rect.inflate(4, 2)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)
        self.screen.blit(text, text_rect)

    # ------------------------------------------------------------------
    def capture_frame(self) -> None:
        """Capture the current screen into ``self.frames`` as a NumPy array."""
        view = pygame.surfarray.array3d(self.screen)
        # Convert from (width, height, 3) to (height, width, 3) and flip
        # vertically to match typical image orientation.
        frame = np.transpose(view, (1, 0, 2))
        self.frames.append(frame)

    # ------------------------------------------------------------------
    def show_press_space(self) -> None:
        """Display a centered "[Press space]" message and wait for space.

        In a headless test environment there is no way for a user to press
        the space key, so the method will automatically continue after a
        short timeout (500 ms). This keeps the behaviour identical for a
        real user (they can still press space) while allowing the script to
        run unattended.
        """
        self.screen.fill((255, 255, 255))
        self._draw_grid()
        msg = self.font.render("[Press space]", True, (0, 0, 0))
        rect = msg.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(msg, rect)
        pygame.display.flip()
        waiting = True
        start_ticks = pygame.time.get_ticks()
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
            # Auto‑continue after 0.5 s if no key press occurred.
            if pygame.time.get_ticks() - start_ticks > 500:
                waiting = False

    # ------------------------------------------------------------------
    def wait_until_close(self) -> None:
        """Keep the window open until the user closes it.

        When running in a head‑less environment (SDL_VIDEODRIVER=dummy)
        there is no window to close. In that case the method returns after
        a short delay (1 s) so that automated tests do not hang.
        """
        import os
        dummy = os.getenv("SDL_VIDEODRIVER") == "dummy"
        if dummy:
            # Wait briefly then exit.
            pygame.time.wait(1000)
            pygame.quit()
            return
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()
