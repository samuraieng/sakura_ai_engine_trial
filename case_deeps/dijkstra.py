"""
ダイクストラアルゴリズムモジュール
迷路の最短経路を計算し、1ステップずつ結果をyieldする
"""
import heapq
from typing import List, Tuple, Optional, Dict, Any
from maze_generator import Maze


# セルの状態
STATE_UNVISITED = 0   # 未訪問（白）
STATE_VISITED = 1     # 訪問済み（赤）…キューに入れた段階
STATE_ADOPTED = 2     # 採用済み（青）…最短距離確定


def dijkstra_steps(maze: Maze,
                   start: Tuple[int, int] = (0, 99),
                   goal: Tuple[int, int] = (99, 0)
                   ) -> Dict[str, Any]:
    """
    ダイクストラアルゴリズムを1ステップずつ実行するジェネレータ

    Maze座標系:
      (0,0) = 左上, (99,99) = 右下
      スタート: (0, HEIGHT-1) = 左下
      ゴール: (WIDTH-1, 0) = 右上

    Yields:
      step_info: {
        'states': 2D配列 (各セルのSTATE_*),
        'step': 現在のステップ数,
        'current': 現在処理中のセル,
        'done': 完了フラグ,
        'path': 最終経路（完了時のみ）,
        'distances': 各セルへの暫定距離,
        'parent': 経路復元用の親セル,
      }
    """
    width, height = maze.width, maze.height
    INF = float('inf')

    # 各セルの状態管理
    states = [[STATE_UNVISITED for _ in range(height)] for _ in range(width)]
    # 距離
    distances = [[INF for _ in range(height)] for _ in range(width)]
    # 親セル（経路復元用）
    parent: List[List[Optional[Tuple[int, int]]]] = [
        [None for _ in range(height)] for _ in range(width)
    ]

    sx, sy = start
    gx, gy = goal

    # スタート地点の初期化
    distances[sx][sy] = 0

    # 優先度付きキュー: (距離, x, y)
    pq = [(0, sx, sy)]
    # キューに投入済みかどうか（重複投入防止）
    in_queue = [[False for _ in range(height)] for _ in range(width)]
    in_queue[sx][sy] = True

    step_count = 0

    while pq:
        d, cx, cy = heapq.heappop(pq)

        # すでにより短い距離で確定済みならスキップ
        if d > distances[cx][cy]:
            continue

        # このセルを「採用（青）」に変更
        changed_cells = []  # このステップで変更されたセル
        if states[cx][cy] != STATE_ADOPTED:
            states[cx][cy] = STATE_ADOPTED
            step_count += 1
            changed_cells.append((cx, cy, STATE_ADOPTED))

        # ゴールに到達したら終了
        if (cx, cy) == (gx, gy):
            yield {
                'states': states,
                'step': step_count,
                'current': (cx, cy),
                'done': False,
                'path': [],
                'changed_cells': changed_cells,
            }
            break

        # 隣接セルを探索
        for nx, ny in maze.get_neighbors(cx, cy):
            new_dist = distances[cx][cy] + 1

            if new_dist < distances[nx][ny]:
                distances[nx][ny] = new_dist
                parent[nx][ny] = (cx, cy)

                if not in_queue[nx][ny]:
                    heapq.heappush(pq, (new_dist, nx, ny))
                    in_queue[nx][ny] = True

                    # 初回発見 → 「訪問（赤）」に変更
                    if states[nx][ny] == STATE_UNVISITED:
                        states[nx][ny] = STATE_VISITED
                        step_count += 1
                        changed_cells.append((nx, ny, STATE_VISITED))

        # 現在の状態をyield
        yield {
            'states': states,
            'step': step_count,
            'current': (cx, cy),
            'done': False,
            'path': [],
            'changed_cells': changed_cells,
        }

    # 経路復元
    path: List[Tuple[int, int]] = []
    if distances[gx][gy] < INF:
        cx, cy = gx, gy
        while (cx, cy) != (sx, sy):
            path.append((cx, cy))
            cx, cy = parent[cx][cy]
        path.append((sx, sy))
        path.reverse()

    # 完了をyield
    yield {
        'states': states,
        'step': step_count,
        'current': None,
        'done': True,
        'path': path,
        'distances': distances,
        'parent': parent,
    }


def reconstruct_path(parent, start, goal):
    """経路を復元する"""
    path = []
    cx, cy = goal
    while (cx, cy) != start:
        path.append((cx, cy))
        cx, cy = parent[cx][cy]
    path.append(start)
    path.reverse()
    return path
