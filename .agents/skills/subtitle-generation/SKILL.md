---
name: subtitle-generation
description: >-
  Generates accurate subtitle streams (subtitles.srt and subtitles.json)
  synchronized with the edited audio transcript.
---

# Subtitle Generation Skill

編集済み音声の再文字起こしデータ（`transcript/edited.json`）に基づき、標準のSRT字幕ファイル（`subtitles/subtitles.srt`）と構造化JSON字幕ファイル（`subtitles/subtitles.json`）を生成します。

## 仕様と出力形式（仕様書 第22章）
字幕はスライドの表示要素（Scene DSL）とは独立して管理され、レンダリング時に動画下部へ焼き込みまたは字幕トラックとして合成されます。

```json
[
  {
    "id": 1,
    "start": 0.0,
    "end": 4.5,
    "text": "今日はAIエージェントについて説明します。"
  }
]
```

## 使用するTools

```bash
# 字幕ファイルの生成 (subtitles.srt と subtitles.json)
uv run python -m tools.cli subtitle_generate <project_dir>/transcript/edited.json <project_dir>/subtitles
```

## 品質ルール
* **1行の文字数**: 1画面あたり最大20〜25文字以内に調整する。
* **表示時間**: 読書速度（1秒あたり4文字程度）を考慮し、最低1.2秒以上表示されるようタイムスタンプを調整する。
* **音声同期**: 発話の開始・終了と±0.15秒以内の精度で同期させる。
