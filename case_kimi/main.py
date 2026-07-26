"""
main.py
ダイクストラ法の迷路探索デモのエントリーポイント。
"""

import sys
import os

# 絶対パスでモジュールを解決（venv 内外どちらでも動作）
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_DIR not in sys.path:
    sys.path.insert(0, _PROJECT_DIR)

import pygame
from maze_generator import generate_maze
from dijkstra import dijkstra_visualizer
from renderer import Renderer


def main():
    SEED = 42
    maze, start, goal = generate_maze(SEED)
    renderer = Renderer(maze, scale=3)

    # ルンニングフラグ（リストで参照渡し）
    running = [True]

    # Space 待機
    if not renderer.show_press_space(running):
        renderer.wait_quit()
        return

    # ダイクストラ実行
    gen = dijkstra_visualizer(maze, start, goal, batch=30)
    state = None

    while running[0]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running[0] = False
                break

        try:
            state = next(gen)
        except StopIteration:
            break

        renderer.draw(
            state["red"],
            state["blue"],
            start,
            goal,
            state["step"],
            saving=False,
        )
        renderer.clock.tick(120)

        if state["done"]:
            break

    # ゴール到達後、最終状態を少し表示してから保存へ
    if state and running[0]:
        renderer.draw(
            state["red"],
            state["blue"],
            start,
            goal,
            state["step"],
            saving=False,
        )
        # 数フレーム待って様子を見せる（録画にも残す）
        for _ in range(30):
            pygame.event.pump()
            renderer.draw(
                state["red"], state["blue"], start, goal, state["step"], saving=False
            )
            renderer.clock.tick(60)

    # GIF 保存（ウィンドウが閉じられる前）
    if running[0]:
        output_path = os.path.join(_PROJECT_DIR, "maze_demo.gif")
        renderer.save_recording(output_path)

        # 保存完了表示
        renderer.screen.fill((30, 30, 30))
        msg = renderer.font_large.render("Saved!", True, (0, 255, 0))
        path_msg = renderer.font_small.render(output_path, True, (255, 255, 255))
        renderer.screen.blit(msg, (renderer.window_w // 2 - 70, renderer.window_h // 2 - 20))
        renderer.screen.blit(path_msg, (renderer.window_w // 2 - 240, renderer.window_h // 2 + 25))
        pygame.display.flip()

        # ウィンドウが閉じられるまで待機
        renderer.wait_quit()


if __name__ == "__main__":
    main()
