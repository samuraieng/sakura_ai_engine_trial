"""
dijkstra.py
ヒープ付きダイクストラ法で最短経路を求め、視覚化用の状態を yield する。
"""

import heapq
from typing import Generator, Dict, Set, Tuple, List


def dijkstra_visualizer(
    maze: List[List[int]],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    batch: int = 40,
) -> Generator[Dict, None, None]:
    """
    ダイクストラ法で迷路を解き、探索過程を可視化する。
    数ステップ (batch) ごとに状態を yield する。

    Yields:
        {
            'red':  Set[Tuple[int, int]],  # 訪問済み（探索候補）
            'blue': Set[Tuple[int, int]],  # 最短経路確定
            'step': int,                   # 床の色変更回数
            'done': bool,                  # ゴール到達フラグ
        }
    """
    height = len(maze)
    width = len(maze[0])
    INF = float("inf")

    # 距離テーブル
    dist = [[INF] * width for _ in range(height)]
    sx, sy = start
    gx, gy = goal
    dist[sy][sx] = 0

    # 優先度付きキュー
    pq = [(0, sx, sy)]

    # 直前のノードを記録（経路復元用）
    prev: Dict[Tuple[int, int], Tuple[int, int]] = {}

    red: Set[Tuple[int, int]] = set()   # 白 -> 赤
    blue: Set[Tuple[int, int]] = set()  # 赤 -> 青（または白 -> 青）
    step_count = 0

    processed = 0
    while pq:
        d, x, y = heapq.heappop(pq)

        # 既に確定済みのノードはスキップ
        if (x, y) in blue:
            continue
        if d > dist[y][x]:
            continue

        # 確定: blue に移行（色変更）
        if (x, y) in red:
            red.remove((x, y))
        blue.add((x, y))
        step_count += 1

        # ゴール到達時、最短経路を辿って blue に加える
        if (x, y) == goal:
            path = []
            cur = (x, y)
            while cur in prev:
                path.append(cur)
                cur = prev[cur]
            path.append(start)

            for node in path:
                if node not in blue:
                    blue.add(node)
                    step_count += 1
            yield {"red": set(red), "blue": set(blue), "step": step_count, "done": True}
            return

        # 隣接ノードを探索（4方向）
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 0:
                nd = d + 1
                if nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    prev[(nx, ny)] = (x, y)
                    heapq.heappush(pq, (nd, nx, ny))

                    # 初めて訪問するなら赤に（色変更）
                    if (nx, ny) not in red and (nx, ny) not in blue:
                        red.add((nx, ny))
                        step_count += 1

        processed += 1
        if processed % batch == 0:
            yield {"red": set(red), "blue": set(blue), "step": step_count, "done": False}

    # 到達不能（完全迷路では通常起こらない）
    yield {"red": set(red), "blue": set(blue), "step": step_count, "done": True}
