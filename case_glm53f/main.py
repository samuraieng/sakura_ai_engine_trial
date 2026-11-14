# -*- coding: utf-8 -*-
"""case_glm53f: 迷路 + ダイクストラ法の可視化デモ (エントリーポイント)。

使い方:
    python main.py [--seed 42] [--auto]

  --seed : 迷路生成のシード値。同じシードなら同じ迷路になる。
           未指定なら毎回ランダムなシードを使う (起動時に表示)。
  --auto : スペースキー待ち / 終了待ちを省略するテスト用モード。
"""
import argparse
import random

from visualizer import main


def parse_args():
    parser = argparse.ArgumentParser(description="Dijkstra maze visualization")
    parser.add_argument("--seed", type=int, default=None,
                        help="迷路生成のシード値 (未指定ならランダム)")
    parser.add_argument("--auto", action="store_true",
                        help="キー待ちを省略するテスト用モード")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    seed = args.seed
    if seed is None:
        seed = random.randrange(2 ** 31)
    print(f"Seed = {seed}")
    main(seed=seed, auto=args.auto)
