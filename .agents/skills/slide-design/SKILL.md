---
name: slide-design
description: >-
  Designs slide layouts and visual hierarchy for each scene using the Scene DSL,
  positioning titles, body copy, cards, diagrams, and asset placeholders.
---

# Slide Design Skill

ストーリーボードに基づき、視聴者の認知負荷を最小化する美しいレイアウトとタイポグラフィ、色彩設計を行い、各シーンごとの `scenes/scene_XXX.json`（Scene DSL）を作成・更新します。

## デザイン原則
1. **1スライド1メッセージ**: 1つのシーンに詰め込みすぎない。
2. **黄金比・余白の確保**: 画面端（セーフエリア：上下左右 100px）には重要要素を配置しない。
3. **洗練されたカラーパレット**:
   - 背景色: 深みのあるダークトーン（`#0f172a`, `#1e293b`）またはクリーンな明色
   - 文字色: コントラストの高い明色（`#f8fafc`, `#94a3b8`）
   - アクセントカラー: ターコイズ（`#06b6d4`）、インディゴ（`#6366f1`）など

## Scene DSL 仕様（仕様書 第18章）

```json
{
  "scene_id": "scene_001",
  "duration": 18.0,
  "background": {
    "type": "solid",
    "color": "#0f172a"
  },
  "elements": [
    {
      "id": "title_text",
      "type": "text",
      "text": "AIエージェントとは？",
      "font_size": 54,
      "color": "#f8fafc",
      "x": 960,
      "y": 380
    },
    {
      "id": "diagram_box",
      "type": "image",
      "asset": "assets/diagrams/arch_overview.png",
      "x": 960,
      "y": 680
    }
  ]
}
```

## 使用するTools

```bash
# シーン新規作成
uv run python -m tools.cli scene_create <project_dir> scene_001 --duration 18.0

# シーン定義の読み込みと検証
uv run python -m tools.cli scene_read <project_dir> scene_001

# シーンの削除
uv run python -m tools.cli scene_delete <project_dir> scene_001
```
