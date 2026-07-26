"""
maze_generator.py
シード固定の穴掘り法で 201×201 の完全迷路を生成する。
壁=1、通路=0。スタートは左下、ゴールは右上。
"""

import random
from typing import List, Tuple


def generate_maze(seed: int, size: int = 100) -> Tuple[List[List[int]], Tuple[int, int], Tuple[int, int]]:
    """
    size x size のセルを持つ迷路を生成する。
    生成される迷路のピクセルサイズは (2*size+1) x (2*size+1)。

    Returns:
        maze: 2次元リスト (0=通路, 1=壁)
        start: (x, y) 左下の通路
        goal:  (x, y) 右上の通路
    """
    rng = random.Random(seed)
    height = 2 * size + 1
    width = 2 * size + 1

    # すべて壁で初期化
    maze = [[1] * width for _ in range(height)]

    # スタート地点（左下の通路ピクセル）
    start_x, start_y = 1, height - 2
    maze[start_y][start_x] = 0

    # 明示的スタックによる深さ優先探索（Pythonの再帰限界を回避）
    stack = [(start_x, start_y)]

    while stack:
        x, y = stack[-1]
        # 上下左右、2マス先を探索
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        rng.shuffle(directions)

        carved = False
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # 2マス先が範囲内かつ未訪問（壁）なら掘る
            if 0 < nx < width - 1 and 0 < ny < height - 1 and maze[ny][nx] == 1:
                # 現在位置と次の位置の間の壁を掘る
                maze[y + dy // 2][x + dx // 2] = 0
                maze[ny][nx] = 0
                stack.append((nx, ny))
                carved = True
                break

        if not carved:
            stack.pop()

    goal_x, goal_y = width - 2, 1
    return maze, (start_x, start_y), (goal_x, goal_y)
