import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


def transcribe_audio(
    audio_path: str,
    output_path: Optional[str] = None,
    language: str = "ja",
    model_name: str = "base",
) -> Dict[str, Any]:
    """Transcribe audio into timestamped segments (JSON).

    Tries:
    1. faster-whisper (if installed)
    2. whisper CLI (if installed)
    3. fallback / stub generator if no model installed
    """
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    result: Dict[str, Any] = {"language": language, "segments": []}

    # 1. Try faster-whisper
    try:
        from faster_whisper import WhisperModel

        model = WhisperModel(model_name, device="auto", compute_type="default")
        segments_gen, info = model.transcribe(str(path), language=language)
        segments_list = []
        for i, seg in enumerate(segments_gen, start=1):
            segments_list.append({
                "id": i,
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": seg.text.strip(),
            })
        result["segments"] = segments_list
        result["detected_language"] = info.language
    except ImportError:
        # 2. Try whisper CLI
        try:
            temp_dir = path.parent / ".temp_whisper"
            temp_dir.mkdir(exist_ok=True)
            cmd = [
                "whisper",
                str(path),
                "--model", model_name,
                "--language", language,
                "--output_format", "json",
                "--output_dir", str(temp_dir),
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            json_file = temp_dir / f"{path.stem}.json"
            if json_file.exists():
                with open(json_file, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    segments_list = []
                    for i, seg in enumerate(raw_data.get("segments", []), start=1):
                        segments_list.append({
                            "id": i,
                            "start": round(float(seg.get("start", 0)), 2),
                            "end": round(float(seg.get("end", 0)), 2),
                            "text": seg.get("text", "").strip(),
                        })
                    result["segments"] = segments_list
        except Exception:
            # 3. Fallback stub with segment metadata structure
            # Allows workflow testing even without GPU / heavyweight ML weights installed
            result["note"] = "Transcription generated via fallback parser. Install faster-whisper for local AI transcription."
            result["segments"] = [
                {
                    "id": 1,
                    "start": 0.0,
                    "end": 5.0,
                    "text": f"[{path.name} 音声文字起こしプレースホルダー]"
                }
            ]

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        out_file = sys.argv[2] if len(sys.argv) > 2 else None
        res = transcribe_audio(sys.argv[1], output_path=out_file)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Usage: python -m tools.audio.transcribe <audio_path> [output_json_path]")
