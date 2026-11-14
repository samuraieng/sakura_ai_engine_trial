# -*- coding: utf-8 -*-
"""迷路の生成を担当するモジュール。

同じシードなら同じ迷路、違うシードなら違う迷路になる (乱数は seed 固定)。
迷路は完全迷路 (すべてのマスがつながる) なのでスタートからゴールへ必ず到達できる。
"""
import numpy as np


class Maze:
    """GRID_N x GRID_N の迷路。セル間の壁を True(壁あり)/False(通路) で管理する。"""

    def __init__(self, grid_n=100, seed=None):
        self.grid_n = grid_n
        self.start = (0, grid_n - 1)      # スタート: 左下固定 (x=0, y=下端)
        self.goal = (grid_n - 1, 0)       # ゴール: 右上固定 (x=右端, y=0)
        self.rng = np.random.RandomState(seed)
        # vwall[y][x]: (x,y) と (x+1,y) の間の縦壁 / hwall[y][x]: (x,y) と (x,y+1) の間の横壁
        self.vwall = np.ones((grid_n, grid_n - 1), dtype=bool)
        self.hwall = np.ones((grid_n - 1, grid_n), dtype=bool)
        self.generate()

    def generate(self):
        """壁伸ばし式の再帰バックトラッキング (スタックベース DFS) で迷路を生成する。"""
        n = self.grid_n
        visited = np.zeros((n, n), dtype=bool)
        sx, sy = self.start
        stack = [(sx, sy)]
        visited[sy][sx] = True
        while stack:
            x, y = stack[-1]
            # 未訪問の隣接セルを集める
            candidates = []
            if x > 0 and not visited[y][x - 1]:
                candidates.append((x - 1, y, "W"))
            if x < n - 1 and not visited[y][x + 1]:
                candidates.append((x + 1, y, "E"))
            if y > 0 and not visited[y - 1][x]:
                candidates.append((x, y - 1, "N"))
            if y < n - 1 and not visited[y + 1][x]:
                candidates.append((x, y + 1, "S"))
            if not candidates:
                stack.pop()  # 行き止まり → バックトラック
                continue
            nx, ny, direction = candidates[self.rng.randint(len(candidates))]
            # 選んだ方向の壁を取り払う
            if direction == "W":
                self.vwall[y][x - 1] = False
            elif direction == "E":
                self.vwall[y][x] = False
            elif direction == "N":
                self.hwall[y - 1][x] = False
            else:
                self.hwall[y][x] = False
            visited[ny][nx] = True
            stack.append((nx, ny))

    def neighbors(self, cell):
        """壁で区切られていない隣接セルのリストを返す。"""
        x, y = cell
        n = self.grid_n
        result = []
        if x > 0 and not self.vwall[y][x - 1]:
            result.append((x - 1, y))
        if x < n - 1 and not self.vwall[y][x]:
            result.append((x + 1, y))
        if y > 0 and not self.hwall[y - 1][x]:
            result.append((x, y - 1))
        if y < n - 1 and not self.hwall[y][x]:
            result.append((x, y + 1))
        return result
