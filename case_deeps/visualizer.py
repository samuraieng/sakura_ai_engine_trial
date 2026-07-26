"""
GUI描画・アニメーション管理モジュール
pygameを使用した迷路可視化と画面更新を担当
"""
import pygame
from typing import Tuple
from maze_generator import Maze


# 色定義
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 50, 50)
COLOR_BLUE = (50, 100, 255)
COLOR_GREEN = (50, 255, 50)
COLOR_DARK_GRAY = (100, 100, 100)

# セルの状態
STATE_UNVISITED = 0
STATE_VISITED = 1
STATE_ADOPTED = 2

# 迷路描画パラメータ（論理サイズ：壁5px、通路1px）
CELL_PATH = 1
CELL_WALL = 5
CELL_UNIT = CELL_PATH + CELL_WALL
MAZE_LOGICAL_SIZE = 100 * CELL_PATH + 101 * CELL_WALL


class Visualizer:
    """迷路の描画と画面管理を行うクラス"""

    def __init__(self, maze: Maze, display_size: int = 320):
        self.maze = maze
        self.display_size = display_size

        self.screen = pygame.display.set_mode((display_size, display_size))
        pygame.display.set_caption("Dijkstra Maze Solver")

        self.logical_surf = pygame.Surface(
            (MAZE_LOGICAL_SIZE, MAZE_LOGICAL_SIZE)
        )

        self._draw_maze_base()

        self.font = pygame.font.Font(None, 24)

    def _draw_maze_base(self) -> None:
        """
        迷路ベースを論理サーフェスに描画
        壁: 黒, 通路（未訪問）: 白
        """
        self.logical_surf.fill(COLOR_BLACK)

        for cx in range(self.maze.width):
            for cy in range(self.maze.height):
                px = CELL_WALL + cx * CELL_UNIT
                py = CELL_WALL + cy * CELL_UNIT

                self.logical_surf.set_at((px, py), COLOR_WHITE)

                if cx < self.maze.width - 1 and not self.maze.vertical_walls[cx][cy]:
                    for dx in range(1, CELL_WALL + 1):
                        self.logical_surf.set_at((px + dx, py), COLOR_WHITE)

                if cy < self.maze.height - 1 and not self.maze.horizontal_walls[cx][cy]:
                    for dy in range(1, CELL_WALL + 1):
                        self.logical_surf.set_at((px, py + dy), COLOR_WHITE)

    def _cell_to_logical(self, cx: int, cy: int) -> Tuple[int, int]:
        """セル座標から論理サーフェス上の座標を返す"""
        return (CELL_WALL + cx * CELL_UNIT, CELL_WALL + cy * CELL_UNIT)

    def update_cell(self, cx: int, cy: int, state: int) -> None:
        """
        セルの色を状態に応じて更新
        0=白(未訪問), 1=赤(通過), 2=青(採用)

        通路（開いた壁）は採用(青)の場合のみ色を塗る。
        通過(赤)の場合はセルピクセルだけを塗り、通路は白のまま。
        """
        color_map = {
            STATE_UNVISITED: COLOR_WHITE,
            STATE_VISITED: COLOR_RED,
            STATE_ADOPTED: COLOR_BLUE,
        }
        color = color_map.get(state, COLOR_WHITE)
        px, py = self._cell_to_logical(cx, cy)

        # セル通路ピクセルを塗る
        self.logical_surf.set_at((px, py), color)

        # 採用(青)の場合のみ、開いた壁（通路）も同じ色で塗る
        if state == STATE_ADOPTED:
            if cx < self.maze.width - 1 and not self.maze.vertical_walls[cx][cy]:
                for dx in range(1, CELL_WALL + 1):
                    self.logical_surf.set_at((px + dx, py), color)
            if cx > 0 and not self.maze.vertical_walls[cx - 1][cy]:
                for dx in range(1, CELL_WALL + 1):
                    self.logical_surf.set_at((px - dx, py), color)
            if cy < self.maze.height - 1 and not self.maze.horizontal_walls[cx][cy]:
                for dy in range(1, CELL_WALL + 1):
                    self.logical_surf.set_at((px, py + dy), color)
            if cy > 0 and not self.maze.horizontal_walls[cx][cy - 1]:
                for dy in range(1, CELL_WALL + 1):
                    self.logical_surf.set_at((px, py - dy), color)

    def draw_step_counter(self, step: int) -> None:
        """右上にStep数を描画"""
        text = self.font.render(f"Step: {step}", True, COLOR_DARK_GRAY)
        text_rect = text.get_rect()
        text_rect.topright = (self.display_size - 4, 4)
        self.screen.blit(text, text_rect)

    def draw_press_space(self) -> None:
        """画面中央に[Press Space]を表示"""
        text = self.font.render("[Press Space]", True, COLOR_DARK_GRAY)
        text_rect = text.get_rect()
        text_rect.center = (self.display_size // 2, self.display_size // 2)
        self.screen.blit(text, text_rect)

    def draw_saving_progress(self, current: int, total: int) -> None:
        """GIF保存中の進捗バーを表示"""
        bar_width = 200
        bar_height = 20
        bar_x = (self.display_size - bar_width) // 2
        bar_y = self.display_size - 50

        pygame.draw.rect(
            self.screen, COLOR_BLACK,
            (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 1
        )
        if total > 0:
            fill_width = int(bar_width * current / total)
            pygame.draw.rect(
                self.screen, COLOR_GREEN,
                (bar_x, bar_y, fill_width, bar_height)
            )
        pct = int(100 * current / total) if total > 0 else 0
        label = self.font.render(f"Saving GIF... {pct}%", True, COLOR_DARK_GRAY)
        label_rect = label.get_rect()
        label_rect.centerx = self.display_size // 2
        label_rect.bottom = bar_y - 4
        self.screen.blit(label, label_rect)

    def draw_done_message(self) -> None:
        """GIF保存完了メッセージを表示"""
        text = self.font.render("Complete!", True, COLOR_GREEN)
        text_rect = text.get_rect()
        text_rect.center = (self.display_size // 2, self.display_size // 2)
        self.screen.blit(text, text_rect)

    def render(self, step: int = 0,
               show_space: bool = False,
               show_saving: bool = False,
               saving_progress: Tuple[int, int] = (0, 0),
               show_done: bool = False) -> pygame.Surface:
        """画面をレンダリングし、サーフェスを返す（GIFキャプチャ用）"""
        scaled = pygame.transform.smoothscale(
            self.logical_surf,
            (self.display_size, self.display_size)
        )
        self.screen.blit(scaled, (0, 0))

        self.draw_step_counter(step)
        if show_space:
            self.draw_press_space()
        if show_saving:
            cur, tot = saving_progress
            self.draw_saving_progress(cur, tot)
        if show_done:
            self.draw_done_message()

        pygame.display.flip()
        return self.screen

    def capture_frame(self) -> pygame.Surface:
        """現在の画面をキャプチャして返す（GIF用）"""
        return self.screen.copy()

    def handle_events(self) -> bool:
        """イベント処理。False=終了"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def wait_for_space(self) -> bool:
        """
        ユーザーがSpaceキーを押すのを待つ
        戻り値: True=Space押下, False=ウィンドウ閉じる
        """
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
        return True

    def wait_until_closed(self) -> None:
        """ユーザーがウィンドウを閉じるまで待機"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

