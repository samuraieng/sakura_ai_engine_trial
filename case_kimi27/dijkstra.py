"""
ダイクストラ法による最短経路探索 + 可視化状態管理。

可視化の色分け：
  - 白：未利用
  - 赤：発見済み（優先度付きキューに入っている候補）
  - 青：採用済み（キューから取り出され、最短距離が確定）
"""

import heapq
from config import GRID_SIZE, START, GOAL


class DijkstraVisualizer:
    """
    ダイクストラ法を1ステップずつ進め、可視化用の状態を更新する。
    """

    def __init__(self, maze):
        self.maze = maze

        # 最短距離と直前セル
        self.dist = [[float('inf')] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.prev = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]

        # 可視化用フラグ
        self.discovered = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.finalized = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]

        # スタート地点を初期化
        sx, sy = START
        self.dist[sy][sx] = 0
        self.discovered[sy][sx] = True
        self.pq = [(0, START)]

        self.done = False
        self.step_count = 0  # main.py で色変更回数として利用

    def step(self) -> bool:
        """
        ダイクストラ法を1ステップ進める。

        Returns:
            bool: まだ続行可能なら True、終了なら False。
        """
        if self.done or not self.pq:
            return False

        d, (x, y) = heapq.heappop(self.pq)

        # 古いエントリ（既に確定済みの距離情報）はスキップ
        if d > self.dist[y][x]:
            return True

        # 確定：赤→青へ変化
        if not self.finalized[y][x]:
            self.finalized[y][x] = True

        # ゴールに到達したら終了
        if (x, y) == GOAL:
            self.done = True
            return False

        # 隣接セルを探索
        for nx, ny in self.maze.neighbors(x, y):
            if self.finalized[ny][nx]:
                continue

            new_dist = d + 1
            if new_dist < self.dist[ny][nx]:
                self.dist[ny][nx] = new_dist
                self.prev[ny][nx] = (x, y)
                heapq.heappush(self.pq, (new_dist, (nx, ny)))

                # 初めて発見されたセルは白→赤へ変化
                if not self.discovered[ny][nx]:
                    self.discovered[ny][nx] = True

        return True

    def get_path(self):
        """
        ゴールからスタートへ遡った最短経路の座標リストを返す。
        （可視化には直接使わず、finalized 状態で青色表示する）
        """
        if self.dist[GOAL[1]][GOAL[0]] == float('inf'):
            return []

        path = []
        x, y = GOAL
        while (x, y) != START:
            path.append((x, y))
            x, y = self.prev[y][x]
        path.append(START)
        path.reverse()
        return path
