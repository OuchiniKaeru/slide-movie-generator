---
name: storyboard-planning
description: >-
  Plans overall video composition and scene boundaries from the edited transcript,
  structuring topics into title, explanation, comparison, and summary scenes in storyboard.json.
---

# Storyboard Planning Skill

編集済み音声の確定文字起こし（`transcript/edited.json`）を読み解き、視聴者が理解しやすいシーン分割と論理展開（起承転結、タイトル・解説・対比・まとめ）を設計して `storyboard/storyboard.json` を生成します。

## ストーリーボード構造（仕様書 第16章）

```json
{
  "project_title": "AI音声動画制作エージェントの解説",
  "total_scenes": 3,
  "scenes": [
    {
      "id": "scene_001",
      "start": 0.0,
      "end": 15.2,
      "purpose": "title",
      "title": "AIエージェントとは？",
      "summary": "AIエージェントの基本定義と全体概要"
    },
    {
      "id": "scene_002",
      "start": 15.2,
      "end": 48.0,
      "purpose": "explanation",
      "title": "自律動作の仕組み",
      "summary": "知覚、判断、実行の3ステップ解説"
    },
    {
      "id": "scene_003",
      "start": 48.0,
      "end": 75.0,
      "purpose": "summary",
      "title": "まとめと今後の展開",
      "summary": "導入メリットと今後の活用領域"
    }
  ]
}
```

## シーン分割のベストプラクティス
1. **1シーンの長さ**: 原則として 10秒〜30秒 を目安とする（短すぎず長すぎず、飽きさせない）。
2. **目的（purpose）の分類**:
   - `title`: オープニング、表紙
   - `concept`: 新規概念の提示
   - `explanation`: 詳細な仕組みやロジック
   - `comparison`: 2つ以上の要素の対比
   - `steps`: 手順、フローチャート
   - `summary`: まとめ、結論
3. **タイムスタンプ整合性**: 前のシーンの `end` と次のシーンの `start` が連続し、全音声区間を網羅すること。
