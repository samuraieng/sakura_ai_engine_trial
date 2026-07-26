"""
エントリポイント
迷路生成 → Space待機 → ダイクストラ実行 → GIF保存 → 終了待機
"""
import os
import random
import pygame
from maze_generator import Maze
from dijkstra import dijkstra_steps
from visualizer import Visualizer
from recorder import save_gif, capture_frames_during_dijkstra


def main():
    # pygame 初期化
    pygame.init()

    # 出力先（このファイルと同じフォルダ）
    output_dir = os.path.dirname(os.path.abspath(__file__))
    gif_path = os.path.join(output_dir, "maze_solve.gif")

    # シード値の設定（日付＋ランダム）
    seed = random.randint(0, 999999)
    print(f"Seed: {seed}")

    # === 迷路生成 ===
    print("Generating maze...")
    maze = Maze(width=100, height=100)
    maze.generate(seed=seed)
    print("Maze generated.")

    # === ビジュアライザ初期化 ===
    viz = Visualizer(maze, display_size=320)

    # === Space待機表示 ===
    viz.render(show_space=True)
    if not viz.wait_for_space():
        pygame.quit()
        return

    # === ダイクストラ実行＆フレームキャプチャ ===
    print("Solving maze with Dijkstra...")
    dijkstra_gen = dijkstra_steps(maze, start=(0, 99), goal=(99, 0))

    # 画面更新・GIFキャプチャの間隔設定
    # 100x100迷路では約20,000ステップ実行されるため、
    # 表示更新は20ステップごと、GIFキャプチャは40ステップごととする
    update_interval = 20
    gif_capture_interval = 40

    frames = capture_frames_during_dijkstra(
        viz, dijkstra_gen,
        update_interval=update_interval,
        gif_capture_interval=gif_capture_interval
    )
    print(f"Captured {len(frames)} frames.")

    # === GIF保存（進捗表示あり） ===
    def progress_callback(current, total):
        # 進捗表示を画面に描画
        viz.render(
            show_saving=True,
            saving_progress=(current, total)
        )
        # pygameイベント処理（終了対応）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

    print(f"Saving GIF to {gif_path}...")
    save_gif(
        frames,
        gif_path,
        duration=0.05,
        progress_callback=progress_callback
    )
    print("GIF saved!")

    # === 完了表示 ===
    viz.render(show_done=True)

    # === ウィンドウが閉じられるまで待機 ===
    viz.wait_until_closed()

    pygame.quit()


if __name__ == "__main__":
    main()
