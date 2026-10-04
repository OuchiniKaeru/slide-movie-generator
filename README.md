# AI音声動画制作エージェント (Tools & Skills)

`仕様書.md` に基づき実装された、動画制作エージェント向けの **Tools（Python / uv 実装）** および **Skills（Antigravity Agent Skills）** の構成です。

---

## 1. ディレクトリ構成

```text
動画作成/
├── 仕様書.md
├── pyproject.toml               # uv環境定義
├── README.md
├── tools/                       # Tool レイヤー (Python / uv)
│   ├── cli.py                   # 統合CLI (エントリーポイント)
│   ├── audio/                   # 音声ツール群
│   │   ├── info.py              # audio_get_info
│   │   ├── transcribe.py        # audio_transcribe
│   │   ├── silence.py           # audio_detect_silence
│   │   ├── filler.py            # audio_detect_filler
│   │   ├── noise.py             # audio_detect_noise
│   │   ├── editor.py            # audio_cut, concat, normalize, denoise
│   │   └── renderer.py          # audio_render (edit_plan適用エンジン)
│   ├── asset/                   # 素材ツール群
│   │   └── asset_tools.py       # asset_search, generate, resize, convert
│   ├── scene/                   # シーンツール群
│   │   └── scene_tools.py       # scene_create, read, update, delete
│   ├── animation/               # アニメーションツール群
│   │   └── animation_tools.py   # animation_add, update, delete
│   ├── subtitle/                # 字幕ツール群
│   │   └── subtitle_tools.py    # subtitle_generate (SRT & JSON)
│   ├── video/                   # レンダリング＆動画ツール群
│   │   └── video_tools.py       # render_scene, render_preview, render_video, inspect, extract_frame
│   └── project/                 # プロジェクト管理ツール
│       └── project_tools.py     # project_init, project_status, project_stage
└── .agents/
    └── skills/                  # Antigravity Skills (プロンプト＆運用指針)
        ├── video-production-agent/   # 全体オーケストレーション
        ├── project-management/       # プロジェクト管理
        ├── audio-analysis/           # 音声解析
        ├── audio-editing/            # 音声編集
        ├── audio-critic/             # 音声品質評価
        ├── storyboard-planning/      # ストーリーボード設計
        ├── slide-design/             # シーンDSL設計
        ├── asset-generation/         # 素材生成・加工
        ├── animation-design/         # アニメーション設定
        ├── subtitle-generation/      # 字幕生成
        ├── video-rendering/          # 動画レンダリング
        └── video-critic/             # 動画品質審査・自動修正ループ
```

---

## 2. 環境構築と実行方法 (`uv`)

本プロジェクトの Python ツールはすべて `uv` で管理・実行します。

### 依存関係の同期
```bash
uv sync
```

### CLI ツールの呼び出し例
統合CLI `tools.cli` を介して、仕様書に定義された全ツールを実行できます。

```bash
# プロジェクト初期化
uv run python -m tools.cli project_init ./projects/demo --audio ./sample.wav

# 音声解析・メタデータ取得
uv run python -m tools.cli audio_get_info ./sample.wav

# 無音区間検出
uv run python -m tools.cli audio_detect_silence ./sample.wav --min-duration 0.8 --threshold-db -40.0

# フィラー検出
uv run python -m tools.cli audio_detect_filler ./projects/demo/transcript/original.json

# 編集計画の適用（非破壊レンダリング）
uv run python -m tools.cli audio_render ./projects/demo/audio/original.wav ./projects/demo/editing/edit_plan.json ./projects/demo/audio/edited.wav

# シーンDSLの作成
uv run python -m tools.cli scene_create ./projects/demo scene_001 --duration 12.0

# プレビュー動画の生成
uv run python -m tools.cli render_preview ./projects/demo

# 最終MP4動画のレンダリング
uv run python -m tools.cli render_video ./projects/demo
```

---

## 3. Skills の役割一覧

| スキル名 | 仕様書参照 | 役割・主な機能 |
| :--- | :--- | :--- |
| `video-production-agent` | 3.1, 33, 38 | 全体ワークフローの統合と各スキルの呼び出しオーケストレーション |
| `project-management` | 5, 29, 30 | ディレクトリ構造初期化、ライフサイクル状態遷移、再実行管理 |
| `audio-analysis` | 6, 7, 14 | 音声メタデータ抽出、無音・フィラー・ノイズ検出、文字起こし |
| `audio-editing` | 8〜13 | `edit_plan.json` による無音短縮・フィラー除去・クロスフェード |
| `audio-critic` | 15 | 編集済み音声の自然さ・単語欠落・音量審査とスコアリング |
| `storyboard-planning` | 16, 39 | 編集後テキストから動画全体の構成・シーン境界・目的を設計 |
| `slide-design` | 17, 18 | `Scene DSL` によるスライドレイアウト、テキスト、配置設計 |
| `asset-generation` | 21 | 図版、イラスト、ダイアグラム、背景画像の生成・リサイズ |
| `animation-design` | 19, 20 | フェード、スライド、強調などのアニメーション付与 |
| `subtitle-generation` | 22 | 音声と同期した `subtitles.srt` および `subtitles.json` の生成 |
| `video-rendering` | 23, 24 | FFmpegを活用したプレビュー動画および最終動画のレンダリング |
| `video-critic` | 25, 26, 40 | プレビュー動画の視覚・同期・文字切れ審査と自動修正ループ判定 |
