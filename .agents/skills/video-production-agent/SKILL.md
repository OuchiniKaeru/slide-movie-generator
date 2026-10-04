---
name: video-production-agent
description: >-
  Orchestrates end-to-end automated video creation from raw input audio.
  Coordinates audio analysis, audio editing, critic reviews, storyboard planning,
  slide design, asset generation, animation, subtitle generation, and final video rendering.
---

# Video Production Agent Skill

入力音声ファイルから高品質な解説動画を一貫して自動生成するマスターワークフロースキルです。
「音声編集 → 内容理解 → ストーリー設計 → スライド生成 → アニメーション → レンダリング → 品質確認」のパイプラインを統括します。

## ワークフロー全体図

```text
1. プロジェクト初期化 (Project Management Skill)
       │
       ▼
2. 音声解析 (Audio Analysis Skill)
       │
       ▼
3. 音声編集計画・実行 (Audio Editing Skill)
       │
       ▼
4. 音声品質審査 (Audio Critic Skill) ──[NG]──> 編集再実行
       │ [OK]
       ▼
5. 編集後再文字起こし (Audio Analysis Skill)
       │
       ▼
6. ストーリーボード設計 (Storyboard Planning Skill)
       │
       ▼
7. スライド＆Scene設計 (Slide Design Skill)
       │
       ▼
8. 素材生成・収集 (Asset Generation Skill)
       │
       ▼
9. アニメーション設定 (Animation Design Skill)
       │
       ▼
10. 字幕生成 (Subtitle Generation Skill)
       │
       ▼
11. プレビューレンダリング (Video Rendering Skill)
       │
       ▼
12. 動画品質審査 (Video Critic Skill) ──[NG]──> 各担当工程へ差し戻し
       │ [OK]
       ▼
13. 最終MP4レンダリング (Video Rendering Skill)
       │
       ▼
14. プロジェクト完了 (Project Management Skill)
```

## 各サブスキルの呼び出しルール

| 工程 | 担当スキル | 主な入力 | 主な出力 |
| :--- | :--- | :--- | :--- |
| 1. プロジェクト管理 | `project-management` | `input/audio.wav` | `project.json` ディレクトリ構成 |
| 2. 音声解析 | `audio-analysis` | `input/audio.wav` | `analysis/audio_info.json`, `transcript/original.json` |
| 3. 音声編集 | `audio-editing` | 解析結果, 元音声 | `editing/edit_plan.json`, `audio/edited.wav` |
| 4. 音声批評 | `audio-critic` | `edited.wav`, 文字起こし | `review/audio_review.json` (スコアと問題点) |
| 5. 再文字起こし | `audio-analysis` | `audio/edited.wav` | `transcript/edited.json` (正式タイムライン) |
| 6. ストーリーボード | `storyboard-planning` | `transcript/edited.json` | `storyboard/storyboard.json` |
| 7. シーン設計 | `slide-design` | ストーリーボード | `scenes/scene_*.json` |
| 8. 素材生成 | `asset-generation` | シーン要素要件 | `assets/` (画像, 図, 背景) |
| 9. アニメーション | `animation-design` | シーン要素 | シーン内 `animations` 定義 |
| 10. 字幕生成 | `subtitle-generation` | `transcript/edited.json` | `subtitles/subtitles.srt`, `subtitles.json` |
| 11. レンダリング | `video-rendering` | シーンDSL, 音声, 字幕 | `render/preview.mp4`, `render/final.mp4` |
| 12. 動画批評 | `video-critic` | `preview.mp4`, シーンDSL | `review/video_review.json` |

## 指示例とエージェントの振る舞い

ユーザー指示：
> inputフォルダの音声から、5分程度の解説動画を作ってください。余分な無音やフィラーを除去し、見やすいビジネス向けスライドにしてください。

エージェントの行動手順：
1. `uv run python -m tools.cli project_init <project_dir> --audio <input_file>` を実行。
2. 仕様書に定義された各工程のスキルを順次実行し、途中成果物（JSON/WAV）を中間形式として保存。
3. Criticスキルによるスコアが合格基準を満たすまで必要最小限の差分修正を実施。
4. 最終MP4を出力し、成果物サマリーを提示する。
