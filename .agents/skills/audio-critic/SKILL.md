---
name: audio-critic
description: >-
  Audits and scores edited audio quality to detect unnatural cuts, word clipping,
  tempo breaks, volume anomalies, or semantic loss, triggering automated re-editing loops.
---

# Audio Critic Skill

編集済み音声（`audio/edited.wav`）と編集計画（`editing/edit_plan.json`）、および新旧文字起こしを対比し、音声の自然さと品質を審査します。

## 評価項目（仕様書 第15章）
1. **不自然なカット**: カット境界でのクリックノイズやブレスの不自然な断絶がないか
2. **単語途中の切断**: 形態素・単語の語頭や語尾が巻き込まれて欠落していないか
3. **不自然な無音**: 会話のリズムを損なう長すぎる無音、または短すぎて機械的な無音がないか
4. **テンポ・話速**: カット後のテンポが急変していないか
5. **音量差・ノイズ**: カット箇所の前後の音圧差が目立っていないか
6. **意味の変化**: 重要な述語や否定詞が削られ、元の意味が歪んでいないか
7. **過剰編集**: 削りすぎて不自然な早口・機械的音声になっていないか

## 審査出力フォーマット (`review/audio_review.json`)

```json
{
  "status": "approved", // または "rejected"
  "score": 0.92,        // 0.0 〜 1.0 (合格基準: >= 0.85)
  "issues": [
    {
      "type": "unnatural_cut",
      "start": 14.2,
      "end": 14.5,
      "severity": "medium",
      "description": "単語の語尾が微小に欠落しているため、クロスフェード幅または終了位置を+0.1s延長してください。"
    }
  ],
  "recommendations": [
    "edit_plan.jsonのoperation #2の終了位置を14.6に変更して再実行"
  ]
}
```

## 自動修正判定
- `score >= 0.85`: 合格（承認）。次の「再文字起こし・ストーリーボード工程」へ進行。
- `score < 0.85`: 不合格。指摘事項を反映して `audio-editing` スキルへ差し戻し。
