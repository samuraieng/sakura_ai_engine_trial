"""
迷路生成モジュール
シードベースで再現可能な100x100迷路を生成する
Recursive Backtracker (Randomized DFS) アルゴリズムを採用
"""
import random
from typing import List, Tuple, Optional


class Maze:
    """迷路データを保持するクラス"""

    def __init__(self, width: int = 100, height: int = 100):
        self.width = width       # 横方向のセル数
        self.height = height     # 縦方向のセル数

        # 壁の管理: True = 壁あり, False = 壁なし(通路)
        # horizontal_walls[x][y]: セル(x,y)とセル(x,y+1)の間の壁
        self.horizontal_walls = [
            [True for _ in range(height - 1)] for _ in range(width)
        ]
        # vertical_walls[x][y]: セル(x,y)とセル(x+1,y)の間の壁
        self.vertical_walls = [
            [True for _ in range(height)] for _ in range(width - 1)
        ]

    def generate(self, seed: int) -> None:
        """指定されたシードで迷路を生成する（同じシード→同じ迷路）"""
        random.seed(seed)
        self._generate_maze()

    def _generate_maze(self) -> None:
        """
        Recursive Backtracker (Randomized DFS) で迷路を生成
        スタート(0,0)から全セルを訪問しながら壁を削除していく
        """
        visited = [[False for _ in range(self.height)] for _ in range(self.width)]

        stack = [(0, 0)]
        visited[0][0] = True

        while stack:
            cx, cy = stack[-1]

            # 未訪問の隣接セルを列挙
            neighbors = []
            # 右
            if cx + 1 < self.width and not visited[cx + 1][cy]:
                neighbors.append((cx + 1, cy, 'right'))
            # 左
            if cx - 1 >= 0 and not visited[cx - 1][cy]:
                neighbors.append((cx - 1, cy, 'left'))
            # 上（y+1）
            if cy + 1 < self.height and not visited[cx][cy + 1]:
                neighbors.append((cx, cy + 1, 'top'))
            # 下（y-1）
            if cy - 1 >= 0 and not visited[cx][cy - 1]:
                neighbors.append((cx, cy - 1, 'bottom'))

            if neighbors:
                # ランダムに隣接セルを選択
                nx, ny, direction = random.choice(neighbors)

                # 壁を削除（通路を開ける）
                if direction == 'right':
                    self.vertical_walls[cx][cy] = False
                elif direction == 'left':
                    self.vertical_walls[cx - 1][cy] = False
                elif direction == 'top':
                    self.horizontal_walls[cx][cy] = False
                elif direction == 'bottom':
                    self.horizontal_walls[cx][cy - 1] = False

                visited[nx][ny] = True
                stack.append((nx, ny))
            else:
                # 行き止まり → バックトラック
                stack.pop()

    def has_wall_between(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        セル(x1,y1)とセル(x2,y2)の間に壁があるかを返す
        隣接していないセル間の問い合わせはエラー
        """
        dx = x2 - x1
        dy = y2 - y1

        # 右隣
        if dx == 1 and dy == 0:
            return self.vertical_walls[x1][y1]
        # 左隣
        elif dx == -1 and dy == 0:
            return self.vertical_walls[x2][y1]
        # 上隣
        elif dx == 0 and dy == 1:
            return self.horizontal_walls[x1][y1]
        # 下隣
        elif dx == 0 and dy == -1:
            return self.horizontal_walls[x1][y2]
        else:
            raise ValueError(f"隣接していないセル: ({x1},{y1}) ↔ ({x2},{y2})")

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """セル(x,y)の通路で繋がっている隣接セルを返す"""
        neighbors = []
        # 右
        if x + 1 < self.width and not self.vertical_walls[x][y]:
            neighbors.append((x + 1, y))
        # 左
        if x > 0 and not self.vertical_walls[x - 1][y]:
            neighbors.append((x - 1, y))
        # 上
        if y + 1 < self.height and not self.horizontal_walls[x][y]:
            neighbors.append((x, y + 1))
        # 下
        if y > 0 and not self.horizontal_walls[x][y - 1]:
            neighbors.append((x, y - 1))
        return neighbors
