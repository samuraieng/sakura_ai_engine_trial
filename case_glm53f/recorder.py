# -*- coding: utf-8 -*-
"""画面描画を GIF として録画・保存するモジュール。

録画サイズは 320x320 以下 (仕様)。
保存中は progress_cb(0.0〜1.0) が随時呼ばれ、進捗を UI に表示できる。
"""
import pygame
import numpy as np
import imageio.v2 as imageio

GIF_SIZE = 320  # 録画の1辺 (320x320 以下)


class GifRecorder:
    """pygame の描画面を切り取って縮小記録し、あとで GIF に書き出す。"""

    def __init__(self, size=GIF_SIZE):
        self.size = size
        self.frames = []  # RGB の numpy 配列 (H, W, 3)

    def capture(self, surface, area=None):
        """画面全体、または area(矩形) を size x size に縮小して 1 フレーム記録する。"""
        if area is not None:
            surface = surface.subsurface(area)
        scaled = pygame.transform.smoothscale(surface, (self.size, self.size))
        # surfarray は (W, H, 3) で返るので (H, W, 3) に転置する
        arr = pygame.surfarray.array3d(scaled).transpose(1, 0, 2)
        self.frames.append(np.ascontiguousarray(arr))

    def save(self, path, fps=20, progress_cb=None):
        """記録したフレームを GIF ファイルへ保存する。

        1 フレームずつ書き出すので、progress_cb でリアルな進捗を報告できる。
        """
        total = len(self.frames)
        writer = imageio.get_writer(path, mode="I", fps=fps, loop=0)
        try:
            for i, frame in enumerate(self.frames):
                writer.append_data(frame)
                if progress_cb:
                    progress_cb((i + 1) / total)
        finally:
            writer.close()
