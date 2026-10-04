---
name: animation-design
description: >-
  Assigns purposeful motion animations (fade, slide, reveal, typewriter, emphasis)
  to scene elements to enhance viewer comprehension without unnecessary distraction.
---

# Animation Design Skill

各シーンのテキストや画像、ダイアグラム要素に対して、発話内容と同期した効果的なアニメーションを設計・設定します。

## アニメーション設計方針（仕様書 第20章）
過剰なアニメーションは避け、説明内容の理解を補助する目的でのみ適用します。

| 伝達内容 | 推奨アニメーション | 目的 |
| :--- | :--- | :--- |
| 新しい概念・タイトルの登場 | `fade_in` / `scale` | 視線を中心へ誘導 |
| 手順・フロー・箇条書き | `reveal` / `typewriter` | 段階的な認知を促す |
| 2項目の比較 | `slide` (左右からイン) | 対比構造の直感的把握 |
| 強調したいキーワード | `emphasis` / `highlight` | 重要ポイントの記憶定着 |
| 因果関係・遷移 | `transition` / `morph` | 状態変化の視覚化 |

## 使用するTools

```bash
# 要素へアニメーションを追加
uv run python -m tools.cli animation_add <project_dir> scene_001 title_text fade_in --start 0.5 --duration 0.8 --easing ease_out

# 比較画像の左右スライドイン追加
uv run python -m tools.cli animation_add <project_dir> scene_002 comp_left slide --start 1.2 --duration 0.6
```

## パラメータ設定ルール
* `start`: シーン開始からの相対秒数（発話のタイミングと厳密に合わせる）。
* `duration`: 基本は 0.4秒〜0.8秒（これ以上長いと間延びし、短いと目が追えない）。
* `easing`: 基本は `ease_out`（自然な減速）。
