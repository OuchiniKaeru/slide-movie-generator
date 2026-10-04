---
name: asset-generation
description: >-
  Searches, generates, resizes, and converts visual assets (diagrams, illustrations,
  backgrounds, and icons) for scenes, maintaining unique project asset IDs.
---

# Asset Generation Skill

シーン設計で必要となる画像素材（ダイアグラム、アイコン、背景、図版、イラスト）を検索・生成・加工し、プロジェクト内の `assets/` フォルダに適切な一意ID（`asset_001` 等）で管理します。

## 素材のカテゴリ分類（仕様書 第21章）
* `assets/images/`: 写真・イラスト
* `assets/icons/`: シンボル・アイコン
* `assets/diagrams/`: 構造図・フローチャート・グラフ
* `assets/generated/`: 自動生成されたプレースホルダーや描画素材

## 使用するTools

```bash
# 既存アセットの検索
uv run python -m tools.cli asset_search <project_dir> --query "diagram"

# ダイアグラムやプレースホルダーアセットの自動生成
uv run python -m tools.cli asset_generate <project_dir> asset_001 --type diagram --text "知覚 → 判断 → 実行" --width 1200 --height 600

# 画像のリサイズ（アスペクト比維持）
uv run python -m tools.cli asset_resize <input_path> <output_path> --width 800 --height 600

# フォーマット変換 (PNG, JPG, WEBP)
uv run python -m tools.cli asset_convert <input_path> <output_path> --format PNG
```

## ガイドライン
* 生成した素材はScene DSLから参照できるように相対パスまたは解決可能なIDで記録する。
* 不必要な高解像度（4K等）はレンダリング負荷を高めるため、動画解像度（フルHD: 1920x1080）に応じた適切なサイズにリサイズする。
