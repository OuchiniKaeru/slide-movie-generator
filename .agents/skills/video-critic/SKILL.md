---
name: video-critic
description: >-
  Audits rendered video preview for audio-video synchronization, text overflow,
  element collisions, animation glitches, and timing correctness, orchestrating targeted auto-fix loops.
---

# Video Critic Skill

生成された動画プレビュー（`preview.mp4`）の映像・音声・タイミング・内容の一致性を総合的に評価し、不具合箇所を特定して該当工程への差し戻しを自動指示します。

## 評価基準（仕様書 第25章）

### 1. 音声品質
* 音声と映像の同期ズレがないか（リップシンク・スライド切り替えタイミング）
* 音声途切れやノイズがないか

### 2. 映像・レイアウト
* 画面端への文字・要素のはみ出し（テキストクリッピング）がないか
* テキストと画像、または図形の不要な重なり（コライダー）がないか
* 解像度やアスペクト比が意図通りか

### 3. タイミングと字幕
* スライド切り替えが話者の話題転換点と一致しているか
* 字幕の出現・消去タイミングが発話と一致しているか

## 使用するTools

```bash
# 動画メタデータ・ストリーム整合性の検証
uv run python -m tools.cli video_inspect <project_dir>/render/preview.mp4

# 不審なタイミングのフレーム画像を抽出して視覚検証
uv run python -m tools.cli video_extract_frame <project_dir>/render/preview.mp4 15.5 <project_dir>/review/frame_15s.jpg
```

## 自動修正ルーティング（仕様書 第26章）

```text
Video Critic 判定
     │
     ├─ 音声ズレ・音量異常 ───> Audio Editing Skill / Audio Render へ差し戻し
     │
     ├─ 文字切れ・重なり ─────> Slide Design Skill (scenes/*.json 修正)
     │
     ├─ アニメーション乱れ ───> Animation Design Skill へ差し戻し
     │
     └─ 全基準合格 (score >= 0.90) ──> Final Video レンダリング許可
```

## 審査レポート出力 (`review/video_review.json`)

```json
{
  "status": "approved", // または "rejected"
  "score": 0.95,
  "issues": [],
  "passed_checks": [
    "audio_sync",
    "no_text_overflow",
    "correct_resolution",
    "subtitle_alignment"
  ]
}
```
