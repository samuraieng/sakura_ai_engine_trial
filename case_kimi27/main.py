"""
ダイクストラ迷路可視化デモのメインエントリ。

動作の流れ：
  1. シード付きで 100x100 の迷路を生成
  2. 画面中央に [Press space] を表示し、space キー入力を待つ
  3. ダイクストラ法を可視化しながら実行
       - 候補セル：赤
       - 確定セル：青
       - 右上に Step 数を表示
  4. ゴール到達後、画面を 320x320 の GIF として保存（進捗バー表示）
  5. ユーザーがウィンドウを閉じるまで待機
"""

import os
import sys

import pygame

from config import (
    GRID_SIZE,
    CELL_UNIT,
    WALL_THICKNESS,
    PATH_THICKNESS,
    LOGICAL_SIZE,
    WINDOW_SIZE,
    COLOR_UNUSED,
    COLOR_VISITED,
    COLOR_ADOPTED,
    COLOR_WALL,
    COLOR_TEXT,
    COLOR_PROGRESS_BG,
    COLOR_PROGRESS_FG,
    WINDOW_FPS,
    UPDATE_EVERY_N_STEPS,
    CAPTURE_EVERY_N_FRAMES,
    SEED,
)
from maze import Maze
from dijkstra import DijkstraVisualizer
from recorder import Recorder


def build_wall_surface(maze: Maze) -> pygame.Surface:
    """迷路の壁を1枚の Surface に描画する（壁は動的に変化しない）。"""
    surface = pygame.Surface(WINDOW_SIZE)
    surface.fill(COLOR_UNUSED)

    # 水平壁
    for h in range(GRID_SIZE + 1):
        for x in range(GRID_SIZE):
            if maze.horizontal_walls[h][x]:
                pygame.draw.rect(
                    surface,
                    COLOR_WALL,
                    (x * CELL_UNIT, h * CELL_UNIT, CELL_UNIT, WALL_THICKNESS),
                )

    # 垂直壁
    for y in range(GRID_SIZE):
        for v in range(GRID_SIZE + 1):
            if maze.vertical_walls[y][v]:
                pygame.draw.rect(
                    surface,
                    COLOR_WALL,
                    (v * CELL_UNIT, y * CELL_UNIT, WALL_THICKNESS, CELL_UNIT),
                )

    return surface



def main():
    pygame.init()
    pygame.display.set_caption("Dijkstra Maze Visualization")
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 24)
    big_font = pygame.font.SysFont(None, 48)

    maze = Maze(SEED)
    dijkstra = DijkstraVisualizer(maze)
    wall_surface = build_wall_surface(maze)

    # 色付きセルを累積描画する透明 Surface（毎フレーム全セルを再描画しない）
    cells_surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
    cells_surface.fill((0, 0, 0, 0))

    cell_colors = [[COLOR_UNUSED for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def set_cell_color(x: int, y: int, color):
        """セルの色を変更し、cells_surface に描画。step_count を増やす。"""
        if cell_colors[y][x] != color:
            cell_colors[y][x] = color
            dijkstra.step_count += 1
            pygame.draw.rect(
                cells_surface,
                color,
                (
                    x * CELL_UNIT + WALL_THICKNESS,
                    y * CELL_UNIT + WALL_THICKNESS,
                    PATH_THICKNESS,
                    PATH_THICKNESS,
                ),
            )

    recorder = Recorder()

    waiting_for_space = True
    solving = False
    solved = False
    save_done = False
    save_progress = 0.0
    frame_counter = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and waiting_for_space:
                    waiting_for_space = False
                    solving = True
                    recorder.start()

        if solving:
            frame_counter += 1
            for _ in range(UPDATE_EVERY_N_STEPS):
                continuing = dijkstra.step()
                if not continuing:
                    solved = True
                    solving = False
                    break

            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    if dijkstra.finalized[y][x]:
                        set_cell_color(x, y, COLOR_ADOPTED)
                    elif dijkstra.discovered[y][x]:
                        set_cell_color(x, y, COLOR_VISITED)

            if frame_counter % CAPTURE_EVERY_N_FRAMES == 0:
                recorder.capture(screen, force=True)

        elif solved and not recorder.saving and not save_done:
            recorder.capture(screen, force=True)
            save_path = os.path.join(os.path.dirname(__file__), "dijkstra_maze.gif")
            recorder.begin_save(save_path)

        elif recorder.saving:
            save_progress = recorder.save_step()
            if save_progress >= 1.0:
                save_done = True

        screen.blit(wall_surface, (0, 0))
        screen.blit(cells_surface, (0, 0))

        step_label = font.render(f"Step: {dijkstra.step_count}", True, COLOR_TEXT)
        screen.blit(step_label, (LOGICAL_SIZE - step_label.get_width() - 10, 10))

        if waiting_for_space:
            text = big_font.render("[Press space]", True, COLOR_TEXT)
            rect = text.get_rect(center=(LOGICAL_SIZE // 2, LOGICAL_SIZE // 2))
            screen.blit(text, rect)
        elif recorder.saving:
            bar_width = 300
            bar_height = 30
            bar_x = (LOGICAL_SIZE - bar_width) // 2
            bar_y = (LOGICAL_SIZE - bar_height) // 2
            pygame.draw.rect(
                screen, COLOR_PROGRESS_BG, (bar_x, bar_y, bar_width, bar_height)
            )
            pygame.draw.rect(
                screen,
                COLOR_PROGRESS_FG,
                (bar_x, bar_y, int(bar_width * save_progress), bar_height),
            )
            save_label = font.render(
                f"Saving GIF... {int(save_progress * 100)}%", True, COLOR_TEXT
            )
            label_rect = save_label.get_rect(center=(LOGICAL_SIZE // 2, bar_y - 20))
            screen.blit(save_label, label_rect)
        elif save_done:
            text = big_font.render("Saved! Close window to exit.", True, COLOR_TEXT)
            rect = text.get_rect(center=(LOGICAL_SIZE // 2, LOGICAL_SIZE // 2))
            screen.blit(text, rect)

        pygame.display.flip()
        clock.tick(WINDOW_FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
