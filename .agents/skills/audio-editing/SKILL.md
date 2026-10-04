---
name: audio-editing
description: >-
  Plans and executes non-destructive audio edits including silence shortening,
  filler removal, repetition/self-correction cutting, normalization, and crossfading via edit_plan.json.
---

# Audio Editing Skill

音声解析結果と文字起こしに基づき、無駄な無音・フィラー・言い直しを除去した編集計画（`edit_plan.json`）を作成し、非破壊で高品質な編集済み音声（`edited.wav`）を書き出します。

## 設計原則（仕様書 第13章 / 第35章）
* **元音声（original.wav）は絶対に上書きしない**。
* すべてのカット・短縮操作は `edit_plan.json` に記録する。
* 各繋ぎ目には 30〜50ms のクロスフェードを施し、プチプチノイズを防止する。
* 文章構造上意味のある「間」は完全に削らず、0.2〜0.3秒程度を保持する（仕様書 第9章）。

## edit_plan.json のフォーマット（仕様書 第12章）

```json
{
  "operations": [
    {
      "type": "trim",
      "start": 12.0,
      "end": 14.5,
      "target_duration": 0.2,
      "reason": "shorten_silence"
    },
    {
      "type": "remove",
      "start": 8.7,
      "end": 10.3,
      "reason": "filler"
    },
    {
      "type": "remove",
      "start": 35.2,
      "end": 42.8,
      "reason": "self_correction"
    }
  ]
}
```

## 使用するTools

```bash
# 編集計画に基づくレンダリング
uv run python -m tools.cli audio_render <project_dir>/audio/original.wav <project_dir>/editing/edit_plan.json <project_dir>/audio/edited.wav --crossfade 40

# 必要に応じた正規化
uv run python -m tools.cli audio_normalize <project_dir>/audio/edited.wav <project_dir>/audio/edited.wav --target-db -1.0

# 必要に応じたノイズ低減
uv run python -m tools.cli audio_denoise <project_dir>/audio/edited.wav <project_dir>/audio/edited.wav
```
