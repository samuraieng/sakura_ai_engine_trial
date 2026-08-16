# Dijkstra Maze Visualization

100×100 のシード付き迷路で、ダイクストラ法による最短経路探索を可視化する Python デモです。

## インストール方法

```bash
cd case_kimi27
./venv/bin/pip install -r requirements.txt
```

初回のみ、仮想環境が未作成の場合は以下で作成してください。

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## 実行方法

```bash
cd case_kimi27
./venv/bin/python main.py
```

1. ウィンドウ中央に `[Press space]` が表示されたら、**Space キー** を押して探索を開始します。
2. ダイクストラ法が可視化され、探索候補が赤、確定（採用）セルが青で表示されます。
3. ゴール到達後、自動的に画面を 320×320 の GIF (`dijkstra_maze.gif`) として保存します。保存中は進捗バーが表示されます。
4. 保存完了後はウィンドウを閉じるまで待機します。

## ファイル説明

| ファイル | 説明 |
| --- | --- |
| `main.py` | エントリポイント。メインループ、描画、イベント処理を担当。 |
| `config.py` | 迷路サイズ、色、FPS、録画設定などの定数を定義。 |
| `maze.py` | シード付き Randomized DFS による 100×100 迷路生成。 |
| `dijkstra.py` | ダイクストラ法の1ステップ実行と可視化状態管理。 |
| `recorder.py` | Pygame 画面のキャプチャと GIF 保存（進捗付き）。 |
| `requirements.txt` | 依存パッケージ一覧。 |

## 仕様のポイント

- 迷路は同じシードに対して常に同じ構造になります（`SEED = 42`）。
- スタート地点は左下、ゴール地点は右上に固定されています。
- 床の色：白（未利用）→ 赤（候補）→ 青（確定/採用）。
- 右上に `Step:` として、床の色が変わった回数をリアルタイム表示。
- 録画 GIF は 320×320 以下に縮小して保存されます。
