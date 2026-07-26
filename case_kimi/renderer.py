"""
renderer.py
Pygame を使った迷路描画、フレーム録画、GIF 保存を担当する。
"""

import os
import pygame
import numpy as np
import imageio
from PIL import Image


class Renderer:
    def __init__(self, maze, scale=3):
        self.maze = maze
        self.h = len(maze)
        self.w = len(maze[0])
        self.scale = scale
        self.logical_h = self.h * scale
        self.logical_w = self.w * scale

        self.window_w = 900
        self.window_h = 950

        pygame.init()
        self.screen = pygame.display.set_mode((self.window_w, self.window_h))
        pygame.display.set_caption("Dijkstra Maze Demo")
        self.font_large = pygame.font.Font(None, 56)
        self.font_small = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

        self.frames = []
        self.last_frame_key = None

        self.colors = {
            "wall": (0, 0, 0),
            "unvisited": (255, 255, 255),
            "red": (255, 0, 0),
            "blue": (0, 0, 255),
            "start": (0, 200, 0),
            "goal": (255, 215, 0),
        }

    def _build_frame_key(self, red_set, blue_set, step):
        return (frozenset(red_set), frozenset(blue_set), step)

    def draw(self, red_set, blue_set, start, goal, step_count, saving=False):
        self.screen.fill((30, 30, 30))
        maze_surf = pygame.Surface((self.logical_w, self.logical_h))

        for y in range(self.h):
            for x in range(self.w):
                if self.maze[y][x] == 1:
                    color = self.colors["wall"]
                elif (x, y) in blue_set:
                    color = self.colors["blue"]
                elif (x, y) in red_set:
                    color = self.colors["red"]
                else:
                    color = self.colors["unvisited"]
                rect = pygame.Rect(x * self.scale, y * self.scale, self.scale, self.scale)
                maze_surf.fill(color, rect)

        sx, sy = start
        gx, gy = goal
        pygame.draw.rect(maze_surf, self.colors["start"],
                         (sx * self.scale, sy * self.scale, self.scale, self.scale))
        pygame.draw.rect(maze_surf, self.colors["goal"],
                         (gx * self.scale, gy * self.scale, self.scale, self.scale))

        offset_x = (self.window_w - self.logical_w) // 2
        offset_y = (self.window_h - self.logical_h) // 2 - 30
        self.screen.blit(maze_surf, (offset_x, offset_y))

        step_text = self.font_small.render(f"Step: {step_count}", True, (255, 255, 255))
        self.screen.blit(step_text, (self.window_w - 180, 20))

        if saving:
            msg = self.font_large.render("Saving GIF...", True, (255, 50, 50))
            self.screen.blit(msg, (self.window_w // 2 - 140, self.window_h - 70))

        pygame.display.flip()

        frame_key = self._build_frame_key(red_set, blue_set, step_count)
        if frame_key != self.last_frame_key:
            self.last_frame_key = frame_key
            frame = pygame.surfarray.array3d(maze_surf)
            frame = np.transpose(frame, (1, 0, 2))
            self.frames.append(frame)

    def save_recording(self, filename="maze_demo.gif"):
        if not self.frames:
            return
        target_size = 320
        frame_count = len(self.frames)
        resized_frames = []
        for i, frame in enumerate(self.frames):
            img = Image.fromarray(frame)
            img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
            resized_frames.append(np.array(img))
            if i % 50 == 0 or i == frame_count - 1:
                progress_text = f"Saving... {int((i + 1) / frame_count * 100)}%"
                self.screen.fill((30, 30, 30))
                msg = self.font_large.render("Saving GIF...", True, (255, 50, 50))
                prog = self.font_small.render(progress_text, True, (255, 255, 255))
                self.screen.blit(msg, (self.window_w // 2 - 140, self.window_h // 2 - 30))
                self.screen.blit(prog, (self.window_w // 2 - 100, self.window_h // 2 + 20))
                pygame.display.flip()
                pygame.event.pump()
        imageio.mimsave(filename, resized_frames, duration=0.05, loop=0)

    def show_press_space(self, running_ref):
        waiting = True
        while waiting and running_ref[0]:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running_ref[0] = False
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
            self.screen.fill((30, 30, 30))
            text = self.font_large.render("[Press space]", True, (255, 255, 255))
            self.screen.blit(text, (self.window_w // 2 - 160, self.window_h // 2))
            pygame.display.flip()
            self.clock.tick(30)
        return True

    def wait_quit(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
            self.clock.tick(30)
        pygame.quit()
