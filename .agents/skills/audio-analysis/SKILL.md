---
name: audio-analysis
description: >-
  Analyzes audio files to extract metadata, detect silence intervals, identify filler words,
  detect noise/clipping, and perform timestamped speech-to-text transcription.
---

# Audio Analysis Skill

入力音声および編集済み音声の音響特性と発話内容を多角的に解析します。

## 解析項目（仕様書 第6章）
* 音声形式・サンプリングレート・チャンネル数・音声長
* 音量（RMS、Peak dB）
* 無音区間（開始・終了・持続時間）
* 発話区間・話速
* フィラー（「えー」「あの」等）の候補抽出
* クリッピング・定常ノイズフロアの検出
* タイムスタンプ付き文字起こし（Whisper形式）

## 使用するTools

```bash
# 1. 音声基本情報・音量取得
uv run python -m tools.cli audio_get_info <audio_path>

# 2. タイムスタンプ付き文字起こし
uv run python -m tools.cli audio_transcribe <audio_path> --output <project_dir>/transcript/original.json --language ja

# 3. 無音区間の検出 (閾値 -40dB, 最小0.8秒)
uv run python -m tools.cli audio_detect_silence <audio_path> --min-duration 0.8 --threshold-db -40.0 --output <project_dir>/analysis/silence.json

# 4. フィラー候補の検出
uv run python -m tools.cli audio_detect_filler <project_dir>/transcript/original.json --output <project_dir>/analysis/fillers.json

# 5. ノイズ・クリッピング検出
uv run python -m tools.cli audio_detect_noise <audio_path> --output <project_dir>/analysis/noise.json
```

## 出力成果物
* `<project_dir>/analysis/audio_info.json`: メタデータ
* `<project_dir>/transcript/original.json`: 初回文字起こし
* `<project_dir>/transcript/edited.json`: 編集済み音声の再文字起こし（**動画制作の正式タイムライン**）
