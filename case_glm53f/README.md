# case_glm53f — 迷路最短経路 (ダイクストラ法) 可視化デモ

100x100 の迷路を生成し、ダイクストラ法による最短経路探索の様子を
pygame の GUI でアニメーション表示するデモです。探索の様子は GIF に録画されます。

## 実行方法

```bash
cd case_glm53f

# venv を使う場合 (初回のみ)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 実行 (シード指定)
python main.py --seed 42

# 実行 (シードをランダムにする。起動時に使用したシードを表示)
python main.py
```

- 起動すると迷路が表示され、画面中央に `[Press space]` と出ます
- **スペースキー**を押すとダイクストラ探索のアニメーションが始まります
  - 探索で通過したマスは **赤** に、最短経路として採用されたマスは **青** に変わります
  - 右上に `Step:` (床の色を変えた回数) が表示されます
- 探索完了後、自動で `maze_solution.gif` (320x320) の保存が始まります
  - 保存中は画面下部に進捗バーが表示されます
- 保存が終わったら、ウィンドウを閉じるまで待機します

### オプション

| オプション | 説明 |
|---|---|
| `--seed N` | 迷路生成のシード値。同じシードなら毎回同じ迷路になる |
| `--auto`   | スペース待ち・終了待ちを省略するテスト用モード |

## インストール方法

必要なパッケージは `requirements.txt` に記載しています。

```bash
pip install -r requirements.txt
```

モジュール判定がうまくいかない場合は、このフォルダの下に venv 環境を作ってください:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 各ファイルの説明

| ファイル | 説明 |
|---|---|
| `main.py` | エントリーポイント。引数解析 (`--seed`, `--auto`) を行い可視化を起動する |
| `maze.py` | 迷路の生成。シード固定の再帰バックトラッキング (DFS) で完全迷路を作る |
| `solver.py` | ダイクストラ法。探索過程をイベント (`visit` / `adopt`) として逐次 yield する |
| `visualizer.py` | pygame による GUI。描画・Step 表示・space 待ち・進捗表示を担当する |
| `recorder.py` | 描画の録画。320x320 に縮小して `maze_solution.gif` に保存する |
| `requirements.txt` | 依存パッケージ (pygame / numpy / imageio) |
| `maze_solution.gif` | 実行時に生成される録画ファイル |

## 仕様メモ

- 迷路サイズ: 100x100 マス。スタートは左下固定、ゴールは右上固定
- 同じシード → 同じ迷路。異なるシード → 異なる迷路
- 床の色: 未利用=白 / 通過=赤 / 採用(最短経路)=青
- 壁: 黒 5px / 通路: 1px (描画ピッチ 8px あたり)
- Step 数: スタートからゴールに到達するまでに床の色を変えた回数 (赤→青の再塗りも 1 回と数える)
- 録画サイズ: 320x320 (GIF)。保存先はこのフォルダ内の `maze_solution.gif`
