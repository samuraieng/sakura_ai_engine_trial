"""
GIF録画モジュール
pygame画面のフレームをキャプチャし、GIFアニメーションとして保存する
"""
import pygame
import imageio
from typing import List


def save_gif(frames: List[pygame.Surface],
             output_path: str,
             duration: float = 0.05,
             progress_callback=None) -> None:
    """
    フレームリストをGIFとして保存する

    Args:
        frames: pygame.Surfaceのリスト
        output_path: 出力先パス
        duration: 1フレームあたりの表示時間（秒）
        progress_callback: 進捗通知用コールバック (current, total)
    """
    total = len(frames)
    if total == 0:
        return

    # imageio用のライターを作成
    writer = imageio.get_writer(output_path, format='GIF', duration=duration, loop=0)

    for i, frame in enumerate(frames):
        # pygame surface → numpy array に変換
        # pygame.surfarray.array3d は (width, height, 3) を返す
        # imageio は (height, width, 3) を期待
        arr = pygame.surfarray.array3d(frame)
        arr = arr.swapaxes(0, 1)  # (W, H, 3) → (H, W, 3)

        writer.append_data(arr)

        if progress_callback:
            progress_callback(i + 1, total)

    writer.close()


def capture_frames_during_dijkstra(visualizer, dijkstra_gen,
                                   update_interval: int = 10,
                                   gif_capture_interval: int = 5) -> List[pygame.Surface]:
    """
    ダイクストラ実行中にフレームをキャプチャする

    Args:
        visualizer: Visualizer インスタンス
        dijkstra_gen: dijkstra_steps のジェネレータ
        update_interval: 画面更新を行うステップ間隔
        gif_capture_interval: GIF用フレームキャプチャのステップ間隔

    Returns:
        frames: キャプチャしたフレームのリスト
    """
    frames = []

    for step_info in dijkstra_gen:
        step = step_info['step']
        done = step_info.get('done', False)
        changed_cells = step_info.get('changed_cells', [])

        # 変更されたセルのみ更新（効率化）
        for cx, cy, state in changed_cells:
            visualizer.update_cell(cx, cy, state)

        # 画面更新（数ステップごと）
        if step % update_interval == 0 or done:
            visualizer.render(step=step)

            # GIF用にキャプチャ（数ステップごと）
            if step % gif_capture_interval == 0 or done:
                frames.append(visualizer.capture_frame())

            # イベント処理（ウィンドウが閉じられたら中断）
            if not visualizer.handle_events():
                break

    # 経路を青で強調表示（最終フレーム追加）
    if 'path' in step_info and step_info['path']:
        path = step_info['path']
        for cx, cy in path:
            visualizer.update_cell(cx, cy, 2)  # 青

        visualizer.render(step=step)
        frames.append(visualizer.capture_frame())

        # 経路のみを表示する最終フレーム（少し間を空ける）
        visualizer.render(step=step)
        frames.append(visualizer.capture_frame())
        visualizer.render(step=step)
        frames.append(visualizer.capture_frame())

    return frames
