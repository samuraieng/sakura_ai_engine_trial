# 迷路ダイクストラ デモ

このリポジトリは、**AGENTS.md** の指示に従って作成した Python デモです。
以下の機能を備えています。

* 100×100 の正方形迷路（シードに依存して決定的に生成）
* スタートは左下、ゴールは右上に固定
* ダイクストラ法で最短経路を探索し、探索過程と最短経路を可視化
* `pygame` によるリアルタイム描画
* 探索中は訪問したセルを **赤**、最短経路は **青** に塗り替え
* 画面右上にステップ数（訪問セル数）を表示
* 開始前に「[Press space]」と表示し、Space キー入力待ち
* アニメーションは **GIF**（320 × 320 ピクセル未満）として保存
* 保存中はプログレスバーで進捗を表示し、完了後はウィンドウを閉じるまで待機

## 必要環境

* Python 3.9 以上
* `pip` でインストール可能な以下のパッケージ

```text
pygame
imageio
numpy
```

## インストール手順

1. **仮想環境の作成（任意）**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows の場合は venv\Scripts\activate
   ```
2. 依存パッケージをインストール
   ```bash
   pip install -r case_oss120/requirements.txt
   ```

## 実行方法

```bash
python -m case_oss120.main   # デフォルトシード 0
```

シードを変えたい場合は `-s` オプションを使用します。

```bash
python -m case_oss120.main -s 42
```

実行するとウィンドウが開き、中央に `[Press space]` と表示されます。Space キーを押すと探索が開始され、探索過程がリアルタイムで描画されます。探索が完了すると、最短経路が青く表示され、`maze_demo.gif`（デフォルト名）という名前で同ディレクトリにアニメーションが保存されます。

ウィンドウはユーザーが閉じるまで残ります。

## ファイル構成

```
case_oss120/
│   main.py          # エントリーポイント
│   maze.py          # 迷路生成・ダイクストラ実装
│   visualizer.py    # pygame を用いた描画・録画ロジック
│   requirements.txt # 必要パッケージ
│   README.md        # 本ドキュメント
```

## 注意事項

* ルートディレクトリ（`/home/masa/sandbox/sakura_ai_engine_trial`）には
  Python ファイルを直接置きません。すべて `case_oss120` 以下に格納しています。
* 生成された GIF のサイズは 300 × 300 ピクセルで、**320 × 320 未満** の制限を満たしています。

---

Enjoy the demo!
