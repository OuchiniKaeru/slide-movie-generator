import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def _format_srt_timestamp(seconds: float) -> str:
    """Format seconds into SRT timestamp HH:MM:SS,mmm."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def generate_subtitles(
    transcript_path: str,
    output_dir: str,
    max_chars_per_line: int = 24,
) -> Dict[str, Any]:
    """Generate subtitles.srt and subtitles.json from transcript."""
    t_path = Path(transcript_path)
    if not t_path.exists():
        raise FileNotFoundError(f"Transcript file not found: {transcript_path}")

    with open(t_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = data.get("segments", [])
    out_base = Path(output_dir)
    out_base.mkdir(parents=True, exist_ok=True)

    srt_path = out_base / "subtitles.srt"
    json_path = out_base / "subtitles.json"

    subtitles_json: List[Dict[str, Any]] = []
    srt_lines: List[str] = []

    for i, seg in enumerate(segments, start=1):
        start = float(seg.get("start", 0))
        end = float(seg.get("end", 0))
        text = seg.get("text", "").strip()

        # Split long text if needed
        subtitles_json.append({
            "id": i,
            "start": start,
            "end": end,
            "text": text,
        })

        srt_lines.append(str(i))
        srt_lines.append(f"{_format_srt_timestamp(start)} --> {_format_srt_timestamp(end)}")
        srt_lines.append(text)
        srt_lines.append("")  # Empty line between entries

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(subtitles_json, f, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "subtitles_count": len(subtitles_json),
        "srt_path": str(srt_path.resolve()),
        "json_path": str(json_path.resolve()),
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3:
        res = generate_subtitles(sys.argv[1], sys.argv[2])
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Usage: python -m tools.subtitle.subtitle_tools <transcript.json> <output_dir>")
