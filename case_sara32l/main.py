import pygame
import random
import heapq
import numpy as np
from PIL import Image
import imageio
import sys

# Constants
GRID_SIZE = 100  # 100x100 logical cells
CELL_SIZE = 3    # pixel size per cell, fits within 320px
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
BLUE = (0,0,255)
FONT_COLOR = (255,255,255)

def generate_maze(N, seed=None):
    """Generate a random maze (passage = True, wall = False).
    The density is controlled by a random threshold; start and goal are forced to be passages."""
    if seed is not None:
        random.seed(seed)
    # 70% of cells become passages (True), 30% become walls (False)
    grid = [[random.random() < 0.7 for _ in range(N)] for _ in range(N)]
    start = (N-1, 0)   # left bottom
    goal = (0, N-1)    # top right
    grid[start[0]][start[1]] = True
    grid[goal[0]][goal[1]] = True
    return grid, start, goal

def dijkstra_stepwise(grid, start, goal):
    """Run Dijkstra stepwise, yielding (x,y) visited order.
    Returns list of visited cells in order and final path."""
    N = len(grid)
    dist = [[float('inf')]*N for _ in range(N)]
    prev = [[None]*N for _ in range(N)]
    dist[start[0]][start[1]] = 0
    pq = [(0, start[0], start[1])]
    visited = []
    while pq:
        d, x, y = heapq.heappop(pq)
        if (x,y) in visited:
            continue
        visited.append((x,y))
        if (x,y) == goal:
            break
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < N and 0 <= ny < N and grid[nx][ny]:
                nd = d + 1
                if nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    prev[nx][ny] = (x,y)
                    heapq.heappush(pq, (nd, nx, ny))
    # reconstruct path
    path = []
    cur = goal
    if dist[goal[0]][goal[1]] != float('inf'):
        while cur is not None:
            path.append(cur)
            cur = prev[cur[0]][cur[1]]
        path.reverse()
    return visited, path

def draw_grid(screen, grid):
    """Draw the entire grid: walls black, passages white."""
    N = len(grid)
    for row in range(N):
        for col in range(N):
            color = WHITE if grid[row][col] else BLACK
            rect = pygame.Rect(col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)

def color_cell(screen, row, col, color):
    """Fill a single cell with given color."""
    rect = pygame.Rect(col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)

def capture_frame(screen):
    """Capture current pygame screen as PIL Image."""
    arr = pygame.surfarray.array3d(screen)
    # Convert from (width, height, 3) to (height, width, 3)
    arr = np.transpose(arr, (1,0,2))
    img = Image.fromarray(arr)
    return img

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Dijkstra Maze Demo")
    font = pygame.font.SysFont(None, 24)

    # Generate maze
    grid, start, goal = generate_maze(GRID_SIZE)

    # Initial draw
    screen.fill(BLACK)
    draw_grid(screen, grid)
    # Show "Press space"
    press_text = font.render("Press SPACE", True, FONT_COLOR)
    text_rect = press_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
    screen.blit(press_text, text_rect)
    pygame.display.flip()

    # Capture initial frame
    frames = [capture_frame(screen)]

    # Wait for space
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

    # Run Dijkstra stepwise
    visited, path = dijkstra_stepwise(grid, start, goal)
    step = 0
    for (x, y) in visited:
        # Color visited cell red (except start)
        if (x, y) != start:
            color_cell(screen, x, y, RED)
            step += 1
        else:
            # start cell already colored white, no step counted
            pass
        # Update step counter display
        screen.fill(BLACK)
        draw_grid(screen, grid)
        # Reapply visited colors up to current
        for vx, vy in visited[:visited.index((x, y))+1]:
            if (vx, vy) != start:
                color_cell(screen, vx, vy, RED)
        # Show step count
        step_text = font.render(f"Step: {step}", True, FONT_COLOR)
        screen.blit(step_text, (WINDOW_WIDTH - step_text.get_width() - 5, 5))
        pygame.display.flip()
        frames.append(capture_frame(screen))
        # Small delay for animation
        pygame.time.wait(50)

    # After visited, draw final path in blue
    for (x, y) in path:
        if (x, y) != start and (x, y) != goal:
            color_cell(screen, x, y, BLUE)
    # Show final step count
    step_text = font.render(f"Step: {step}", True, FONT_COLOR)
    screen.blit(step_text, (WINDOW_WIDTH - step_text.get_width() - 5, 5))
    pygame.display.flip()
    frames.append(capture_frame(screen))

    # Save gif
    print("Saving gif...")
    # Convert frames to list of numpy arrays
    img_arrays = [np.array(f) for f in frames]
    imageio.mimsave('maze_solution.gif', img_arrays, fps=10)
    print("Saved maze_solution.gif")

    # Wait until user closes window
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()

if __name__ == "__main__":
    main()