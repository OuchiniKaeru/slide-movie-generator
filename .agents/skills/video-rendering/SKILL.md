---
name: video-rendering
description: >-
  Renders individual scenes, low-resolution fast preview videos (preview.mp4),
  and final production MP4 videos (final.mp4) with audio and subtitles combined.
---

# Video Rendering Skill

Scene DSL、アニメーション設定、編集済み音声、字幕を合成し、FFmpegまたはレンダリングエンジンを駆動して動画ファイルを生成します。

## レンダリングパイプライン（仕様書 第23章 / 第24章）

```text
Scene DSL
   +
Animation
   +
Subtitle
   +
Edited Audio
    │
    ▼
 Renderer (FFmpeg / Engine)
    │
    ├─ 1. 低解像度 preview.mp4 (960x540) ──> Video Critic 審査
    │
    └─ 2. 最終高画質 final.mp4 (1920x1080)
```

## 使用するTools

```bash
# 1. 単一シーンのレンダリング（動作確認用）
uv run python -m tools.cli render_scene <project_dir> scene_001

# 2. 低解像度プレビュー動画の高速生成
uv run python -m tools.cli render_preview <project_dir>

# 3. 最終高画質MP4の完全レンダリング (フルHD 1920x1080, 30fps)
uv run python -m tools.cli render_video <project_dir>
```

## 設計原則（仕様書 第35章 原則3）
* **AIとRendererを完全に分離する**: AI自身が低レベルのコマンド文字列を複雑に自作せず、統一されたRenderer Toolを呼び出す。
* まずプレビュー（`preview.mp4`）を作成し、Video Criticのチェックをパスしてから最終書き出しを行う。
