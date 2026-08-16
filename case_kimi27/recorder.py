"""
画面キャプチャから GIF 動画を保存するモジュール。

- pygame サーフェスを 320x320 に縮小
- imageio を使って GIF 形式で保存
- 保存処理を細切れに行い、進捗率を返す（メインループで進捗バーを表示）
"""

import imageio
import numpy as np
import pygame
from config import GIF_SIZE, RECORDER_FPS


class Recorder:
    """Pygame 画面の録画と GIF 保存を行う。"""

    def __init__(self, size: tuple = GIF_SIZE, fps: int = RECORDER_FPS):
        self.size = size
        self.fps = fps
        self.frames = []
        self.writer = None
        self.saving = False
        self.save_index = 0
        self.total_frames = 0
        self.save_path = ""

    def start(self):
        """録画を開始する。"""
        self.frames = []

    def capture(self, surface: pygame.Surface, force: bool = False):
        """
        現在の画面をフレームとして記録する。

        Args:
            surface: キャプチャ対象の pygame Surface。
            force: True の場合、毎回記録する。False の場合は呼び出し側が
                   フレーム間引きを制御する想定。
        """
        if not force and not self.frames and not self.saving:
            return
        scaled = pygame.transform.smoothscale(surface, self.size)
        arr = pygame.surfarray.array3d(scaled)  # shape: (w, h, 3)
        # imageio は (h, w, 3) を期待するので転置
        arr = np.transpose(arr, (1, 0, 2))
        self.frames.append(arr)

    def begin_save(self, path: str):
        """GIF 保存を開始する。"""
        self.writer = imageio.get_writer(path, mode='I', fps=self.fps)
        self.save_index = 0
        self.total_frames = len(self.frames)
        self.saving = True
        self.save_path = path

    def save_step(self) -> float:
        """
        1フレーム分の GIF 書き出しを進める。

        Returns:
            float: 0.0～1.0 の進捗率。保存完了時は 1.0 を返す。
        """
        if not self.saving:
            return 1.0

        self.writer.append_data(self.frames[self.save_index])
        self.save_index += 1

        if self.save_index >= self.total_frames:
            self.writer.close()
            self.saving = False
            return 1.0

        return self.save_index / self.total_frames
