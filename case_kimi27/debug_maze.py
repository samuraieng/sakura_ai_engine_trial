"""
80%進捗時点の迷路状態を PNG 画像で出力し、内部状態を分析するデバッグスクリプト。
pygame を使わずに PIL で描画するため、ヘッドレス環境でも動作する。
"""

import os
from PIL import Image

from config import (
    GRID_SIZE,
    CELL_UNIT,
    WALL_THICKNESS,
    PATH_THICKNESS,
    LOGICAL_SIZE,
    COLOR_UNUSED,
    COLOR_VISITED,
    COLOR_ADOPTED,
    COLOR_WALL,
    SEED,
    START,
    GOAL,
)
from maze import Maze
from dijkstra import DijkstraVisualizer


def draw_state(maze: Maze, dijkstra: DijkstraVisualizer, path: str) -> None:
    """現在のダイクストラ状態を論理サイズの PNG に保存する。"""
    img = Image.new("RGB", (LOGICAL_SIZE, LOGICAL_SIZE), COLOR_UNUSED)
    pixels = img.load()

    # 壁を描画
    for h in range(GRID_SIZE + 1):
        for x in range(GRID_SIZE):
            if maze.horizontal_walls[h][x]:
                for dx in range(CELL_UNIT):
                    px = x * CELL_UNIT + dx
                    py = h * CELL_UNIT
                    for dy in range(WALL_THICKNESS):
                        if 0 <= px < LOGICAL_SIZE and 0 <= py + dy < LOGICAL_SIZE:
                            pixels[px, py + dy] = COLOR_WALL

    for y in range(GRID_SIZE):
        for v in range(GRID_SIZE + 1):
            if maze.vertical_walls[y][v]:
                for dy in range(CELL_UNIT):
                    px = v * CELL_UNIT
                    py = y * CELL_UNIT + dy
                    for dx in range(WALL_THICKNESS):
                        if 0 <= px + dx < LOGICAL_SIZE and 0 <= py < LOGICAL_SIZE:
                            pixels[px + dx, py] = COLOR_WALL

    # 色付きセルを描画
    visited_count = 0
    adopted_count = 0
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            px = x * CELL_UNIT + WALL_THICKNESS
            py = y * CELL_UNIT + WALL_THICKNESS
            if dijkstra.finalized[y][x]:
                color = COLOR_ADOPTED
                adopted_count += 1
            elif dijkstra.discovered[y][x]:
                color = COLOR_VISITED
                visited_count += 1
            else:
                continue
            # 1px では目に見えないため、可視化用に 3x3 の点で描画
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    qx, qy = px + dx, py + dy
                    if 0 <= qx < LOGICAL_SIZE and 0 <= qy < LOGICAL_SIZE:
                        pixels[qx, qy] = color

    # スタートとゴールのマーカー（やや大きめに）
    for x, y, color in [(START[0], START[1], (0, 255, 0)), (GOAL[0], GOAL[1], (255, 255, 0))]:
        cx = x * CELL_UNIT + WALL_THICKNESS
        cy = y * CELL_UNIT + WALL_THICKNESS
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                px, py = cx + dx, cy + dy
                if 0 <= px < LOGICAL_SIZE and 0 <= py < LOGICAL_SIZE:
                    pixels[px, py] = color

    img.save(path)
    total_cells = GRID_SIZE * GRID_SIZE
    print(f"saved: {path}")
    print(f"  visited(赤): {visited_count}")
    print(f"  adopted(青): {adopted_count}")
    print(f"  total colored: {visited_count + adopted_count} / {total_cells} "
          f"({100 * (visited_count + adopted_count) / total_cells:.1f}%)")


def main():
    maze = Maze(SEED)
    dijkstra = DijkstraVisualizer(maze)

    total_cells = GRID_SIZE * GRID_SIZE
    target_progress = 0.80

    step = 0
    while True:
        continuing = dijkstra.step()
        step += 1
        colored = sum(
            1 for y in range(GRID_SIZE) for x in range(GRID_SIZE)
            if dijkstra.discovered[y][x] or dijkstra.finalized[y][x]
        )
        progress = colored / total_cells
        if progress >= target_progress or not continuing:
            print(f"step={step}, progress={progress:.1%}")
            out_path = os.path.join(os.path.dirname(__file__), "debug_state.png")
            draw_state(maze, dijkstra, out_path)
            break


if __name__ == "__main__":
    main()
