# -*- coding: utf-8 -*-
"""迷路とダイクストラ探索の様子を pygame で可視化するモジュール。

フェーズ遷移: wait(待機) → solve(探索アニメ) → save(GIF保存) → done(完了待ち)
"""
import os
import sys
import pygame
import numpy as np

from maze import Maze
from solver import dijkstra_steps
from recorder import GifRecorder

# ---------------- 描画パラメータ ----------------
GRID_N = 100              # 迷路の1辺のマス数 (100x100)
PITCH = 8                 # 1マスあたりのピッチ (px)
WALL_PX = 5               # 壁の太さ (px)
PATH_PX = 1               # 通路の太さ (px)
MAZE_PX = PITCH * GRID_N  # 迷路本体の描画サイズ (800px)
MARGIN_X = 15             # 迷路の左右の余白
TOP_UI = 55               # 上部UI (Step 表示) の高さ
BOTTOM_UI = 45            # 下部UI (状態 / 進捗バー) の高さ
WIN_W = MAZE_PX + MARGIN_X * 2
WIN_H = MAZE_PX + TOP_UI + BOTTOM_UI
EVENTS_PER_FRAME = 5      # 1フレームで処理する探索イベント数 (描画の動的更新用)
FRAME_EVERY = 50          # 何マスの探索ごとに録画するか
ADOPT_EVERY = 10          # 採用(青)イベントを何個おきに録画するか

# ---------------- 色定義 ----------------
COL_BG    = (190, 190, 190)  # 迷路の外側の背景
COL_FLOOR = (255, 255, 255)  # 未利用の床: 白
COL_PASS  = (255, 0, 0)      # 通過した床: 赤
COL_ADOPT = (0, 0, 255)      # 採用(最短経路)の床: 青
COL_WALL  = (0, 0, 0)        # 壁: 黒

FLOOR_UNUSED, FLOOR_PASS, FLOOR_ADOPT = 0, 1, 2


class MazeApp:
    """アプリ本体。wait → solve → save → done の順に進む。"""

    def __init__(self, seed=None, auto=False):
        self.auto = auto  # テスト用: 待ちを省略して自動進行する
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Dijkstra Maze - case_glm53f")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 26)
        self.font_big = pygame.font.SysFont(None, 52)
        self.maze = Maze(grid_n=GRID_N, seed=seed)
        self.recorder = GifRecorder()
        self.floor = np.zeros((GRID_N, GRID_N), dtype=np.uint8)  # 床の状態
        self.step_count = 0        # 床の色を変えた回数 (=Step)
        self.visits = 0            # 探索で通過したマス数
        self.adopts = 0            # 採用イベントの処理数
        self.phase = "wait"
        self.save_progress = 0.0
        self.gif_path = ""
        self.maze_rect = pygame.Rect(MARGIN_X, TOP_UI, MAZE_PX, MAZE_PX)

    # ---------- 床の色管理 ----------
    def paint(self, cell, code):
        """床の色を変える。実際に変化した場合のみ Step をカウントする。"""
        x, y = cell
        if self.floor[y][x] != code:
            self.floor[y][x] = code
            self.step_count += 1

    # ---------- 描画 ----------
    def draw(self):
        """現在の状態に応じて画面全体を描画する。"""
        self.screen.fill(COL_BG)
        pygame.draw.rect(self.screen, COL_FLOOR, self.maze_rect)  # 迷路の下地 (白)
        self._draw_floors()
        self._draw_walls()
        self._draw_step()
        self._draw_status()
        if self.phase == "wait":
            self._blit_center("[Press space]", self.font_big, COL_WALL)

    def _cell_rect(self, x, y):
        """セル内部の矩形 (7x7px)。壁 5px と通路 1px を残す配置。"""
        return (MARGIN_X + x * PITCH + 1, TOP_UI + y * PITCH + 1,
                PITCH - PATH_PX, PITCH - PATH_PX)

    def _draw_floors(self):
        """色が付いた床 (赤=通過 / 青=採用) を描く。"""
        ys, xs = np.nonzero(self.floor)
        for x, y in zip(xs, ys):
            col = COL_PASS if self.floor[y][x] == FLOOR_PASS else COL_ADOPT
            self.screen.fill(col, self._cell_rect(x, y))

    def _draw_walls(self):
        """内部の壁を 5px の黒線で描く (通路側は 1px の隙間がそのまま白く見える)。"""
        off = (PITCH - WALL_PX) // 2 + 1  # 壁線のセル内オフセット
        for y in range(GRID_N):
            base_y = TOP_UI + y * PITCH
            row = self.maze.vwall[y]
            for x in np.nonzero(row)[0]:
                gx = MARGIN_X + int(x) * PITCH + off
                pygame.draw.rect(self.screen, COL_WALL, (gx, base_y, WALL_PX, PITCH))
        for y in range(GRID_N - 1):
            base_y = TOP_UI + y * PITCH + off
            row = self.maze.hwall[y]
            for x in np.nonzero(row)[0]:
                gx = MARGIN_X + int(x) * PITCH
                pygame.draw.rect(self.screen, COL_WALL, (gx, base_y, PITCH, WALL_PX))
        # 外周の壁
        pygame.draw.rect(self.screen, COL_WALL, self.maze_rect, WALL_PX)

    def _draw_step(self):
        """右上に Step 数を表示する。"""
        surf = self.font.render(f"Step: {self.step_count}", True, COL_WALL)
        self.screen.blit(surf, surf.get_rect(topright=(WIN_W - 12, 12)))

    def _draw_status(self):
        """下部に状態メッセージと (保存中は) 進捗バーを表示する。"""
        if self.phase == "solve":
            msg = "Searching... (Dijkstra)"
        elif self.phase == "save":
            msg = f"Saving GIF... {self.save_progress * 100:.0f}%"
        elif self.phase == "done":
            msg = f"Done!  Step={self.step_count}  Saved: {os.path.basename(self.gif_path)}"
        else:
            msg = "Ready. Press SPACE to start."
        surf = self.font.render(msg, True, COL_WALL)
        self.screen.blit(surf, (MARGIN_X, WIN_H - BOTTOM_UI + 6))
        if self.phase == "save":
            self._draw_progress_bar()

    def _draw_progress_bar(self):
        """GIF 保存中の進捗バー。"""
        bw, bh = 400, 14
        bx, by = (WIN_W - bw) // 2, WIN_H - 22
        pygame.draw.rect(self.screen, (120, 120, 120), (bx, by, bw, bh), 1)
        filled = int((bw - 4) * self.save_progress)
        if filled > 0:
            pygame.draw.rect(self.screen, (0, 150, 0), (bx + 2, by + 2, filled, bh - 4))

    def _blit_center(self, text, font, color):
        """迷路の中央に文字を描く。"""
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=self.maze_rect.center))

    def _pump_quit(self):
        """QUIT イベントが来たら即終了する (探索/保存中のフリーズ防止)。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

    # ---------- 各フェーズ ----------
    def run_wait(self):
        """スペースキーが押されるまで待機する。"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.phase = "solve"
                    return True
            self.draw()
            pygame.display.flip()
            self.clock.tick(30)

    def run_solve(self):
        """ダイクストラの探索過程をアニメーション表示しながら録画する。

        録画は描画 (draw + flip) の後に行う。そうしないと
        画面より前の状態を撮ってしまい、同一フレームばかりになるため。
        """
        gen = dijkstra_steps(self.maze)
        speed = 50 if self.auto else EVENTS_PER_FRAME
        finished = False
        while not finished:
            self._pump_quit()
            need_capture = False
            for _ in range(speed):
                try:
                    kind, cell = next(gen)
                except StopIteration:
                    finished = True
                    break
                self.paint(cell, FLOOR_PASS if kind == "visit" else FLOOR_ADOPT)
                if kind == "visit":
                    self.visits += 1
                    if self.visits % FRAME_EVERY == 0:  # 数ステップごとに録画
                        need_capture = True
                else:  # 採用 (青) も数イベントおきに録画
                    self.adopts += 1
                    if self.adopts % ADOPT_EVERY == 0:
                        need_capture = True
            self.draw()  # 数ステップごとに描画を更新
            pygame.display.flip()
            if need_capture:  # 描画後の最新画面を録画する
                self.recorder.capture(self.screen, self.maze_rect)
            if not self.auto:
                self.clock.tick(120)
        # 完成した最終状態を録画
        self.draw()
        pygame.display.flip()
        self.recorder.capture(self.screen, self.maze_rect)
        self.recorder.capture(self.screen, self.maze_rect)
        self.phase = "save"

    def run_save(self):
        """録画したフレームを GIF へ保存する (進捗を表示しながら)。"""
        base = os.path.dirname(os.path.abspath(__file__))
        self.gif_path = os.path.join(base, "maze_solution.gif")
        self.recorder.save(self.gif_path, fps=20, progress_cb=self._on_save_progress)
        self.phase = "done"

    def _on_save_progress(self, progress):
        """保存の進捗を受け取り、画面を更新する。"""
        self.save_progress = progress
        self.draw()
        pygame.display.flip()
        self._pump_quit()

    def run_done(self):
        """完了表示。ユーザーが画面を閉じるまで待機する。"""
        if self.auto:  # テスト用: 自動で閉じる
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
            self.draw()
            pygame.display.flip()
            self.clock.tick(30)

    # ---------- メインループ ----------
    def run(self):
        if self.auto:
            self.phase = "solve"  # 待機を省略
        while True:
            if self.phase == "wait":
                if not self.run_wait():
                    break
            elif self.phase == "solve":
                self.run_solve()
            elif self.phase == "save":
                self.run_save()
            else:
                if not self.run_done():
                    break
        pygame.quit()


def main(seed=None, auto=False):
    """可視化アプリを起動する。"""
    MazeApp(seed=seed, auto=auto).run()
