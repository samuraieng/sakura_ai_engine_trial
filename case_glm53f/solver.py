# -*- coding: utf-8 -*-
"""ダイクストラ法による最短経路探索モジュール。

探索の進行をイベントとして逐次 yield するので、
呼び出し側はそれを 1 件ずつ描画に反映できる。
"""
import heapq


def dijkstra_steps(maze):
    """スタートからゴールまでダイクストラ法で探索する。

    yield するイベント:
      ("visit", cell) ... 探索で通過したマス (床を赤に変える)
      ("adopt", cell) ... 最短経路として採用されたマス (床を青に変える)
    """
    start, goal = maze.start, maze.goal
    dist = {start: 0}
    prev = {}
    done = set()
    heap = [(0, start)]
    while heap:
        d, cur = heapq.heappop(heap)
        if cur in done:
            continue
        done.add(cur)
        yield ("visit", cur)
        if cur == goal:
            break
        for nb in maze.neighbors(cur):
            nd = d + 1
            if nb not in dist or nd < dist[nb]:
                dist[nb] = nd
                prev[nb] = cur
                heapq.heappush(heap, (nd, nb))

    # ゴールから逆にたどって経路を復元し、スタート順で採用イベントを出す
    path = []
    c = goal
    while c != start:
        path.append(c)
        c = prev[c]
    path.append(start)
    for cell in reversed(path):
        yield ("adopt", cell)
