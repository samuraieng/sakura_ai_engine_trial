"""
シード付き迷路生成モジュール。

ランダム化深さ優先探索（Randomized DFS）を用いて、
100x100 の完全迷路を生成する。
同じシードに対しては常に同じ迷路が得られる。
"""

import random
from config import GRID_SIZE, START


class Maze:
    """壁情報を保持する迷路クラス。"""

    def __init__(self, seed: int):
        self.seed = seed
        self.rng = random.Random(seed)

        # horizontal_walls[h][x]
        #   h = 0..GRID_SIZE の水平壁番号（0が上境界、GRID_SIZEが下境界）
        #   x = 0..GRID_SIZE-1 の列
        self.horizontal_walls = [
            [True] * GRID_SIZE for _ in range(GRID_SIZE + 1)
        ]

        # vertical_walls[y][v]
        #   y = 0..GRID_SIZE-1 の行
        #   v = 0..GRID_SIZE の垂直壁番号（0が左境界、GRID_SIZEが右境界）
        self.vertical_walls = [
            [True] * (GRID_SIZE + 1) for _ in range(GRID_SIZE)
        ]

        self._generate()

    # -----------------------------------------------------------------------
    # 迷路生成（Randomized DFS）
    # -----------------------------------------------------------------------
    def _generate(self):
        visited = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
        stack = [START]
        sx, sy = START
        visited[sy][sx] = True

        while stack:
            x, y = stack[-1]
            neighbors = []
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if not visited[ny][nx]:
                        neighbors.append((nx, ny, dx, dy))

            if neighbors:
                nx, ny, dx, dy = self.rng.choice(neighbors)
                visited[ny][nx] = True
                self._remove_wall(x, y, dx, dy)
                stack.append((nx, ny))
            else:
                stack.pop()

    def _remove_wall(self, x: int, y: int, dx: int, dy: int):
        """セル (x, y) から (dx, dy) 方向へ移動する壁を取り除く。"""
        if dx == 1:       # 右へ移動：右側の垂直壁を除去
            self.vertical_walls[y][x + 1] = False
        elif dx == -1:    # 左へ移動：左側の垂直壁を除去
            self.vertical_walls[y][x] = False
        elif dy == 1:     # 下へ移動：下側の水平壁を除去
            self.horizontal_walls[y + 1][x] = False
        elif dy == -1:    # 上へ移動：上側の水平壁を除去
            self.horizontal_walls[y][x] = False

    # -----------------------------------------------------------------------
    # 移動判定
    # -----------------------------------------------------------------------
    def can_move(self, x: int, y: int, dx: int, dy: int) -> bool:
        """セル (x, y) から (dx, dy) 方向へ移動可能か。"""
        nx, ny = x + dx, y + dy
        if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
            return False

        if dx == 1:
            return not self.vertical_walls[y][x + 1]
        if dx == -1:
            return not self.vertical_walls[y][x]
        if dy == 1:
            return not self.horizontal_walls[y + 1][x]
        if dy == -1:
            return not self.horizontal_walls[y][x]
        return False

    def neighbors(self, x: int, y: int):
        """セル (x, y) から移動可能な隣接セルのリストを返す。"""
        result = []
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            if self.can_move(x, y, dx, dy):
                result.append((x + dx, y + dy))
        return result
