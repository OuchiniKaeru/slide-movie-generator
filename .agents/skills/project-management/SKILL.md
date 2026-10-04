---
name: project-management
description: >-
  Manages video production project directory layout, project.json lifecycle states,
  configuration settings, step re-execution, and artifact tracking.
---

# Project Management Skill

動画制作プロジェクトのライフサイクル、ディレクトリ構造、設定、状態管理、および工程ごとの再実行を管理します。

## プロジェクト構造（仕様書 第5章）

```text
project_001/
├── input/             # 元音声ファイル
├── analysis/          # 音声情報、解析結果
├── transcript/        # original.json, edited.json
├── audio/             # original.wav, edited.wav, preview.wav
├── editing/           # edit_plan.json
├── storyboard/        # storyboard.json
├── scenes/            # scene_001.json, scene_002.json...
├── assets/            # images, icons, diagrams, generated
├── subtitles/         # subtitles.srt, subtitles.json
├── render/            # preview.mp4, final.mp4
├── review/            # audio_review.json, video_review.json
└── project.json       # プロジェクト設定と現在ステータス
```

## 使用するTools

```bash
# プロジェクト初期化
uv run python -m tools.cli project_init <project_dir> [--audio <source_audio>]

# プロジェクト状態確認
uv run python -m tools.cli project_status <project_dir>

# ステージ更新
uv run python -m tools.cli project_stage <project_dir> <stage_name>
```

## ステージ一覧
- `created`: 初期化完了
- `analyzing`: 音声解析中
- `editing_audio`: 音声編集計画・実行中
- `reviewing_audio`: 音声批評審査中
- `planning`: ストーリーボード設計中
- `designing`: スライド・素材・アニメーション設計中
- `rendering`: レンダリング中
- `reviewing_video`: 動画批評審査中
- `completed`: 全工程完了
- `failed`: エラー中断

## 再実行コマンド規約（仕様書 第30章）
特定の工程のみを再実行する場合：
- `/audio`: 音声解析・編集のみ再実行
- `/storyboard`: ストーリー構成のみ再構築
- `/scenes`: スライドレイアウトのみ再生成
- `/animation`: アニメーション設定のみ更新
- `/render`: 動画レンダリングのみ再実行
