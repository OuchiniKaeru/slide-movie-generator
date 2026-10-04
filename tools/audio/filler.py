import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_FILLERS = [
    "えー", "えーっと", "ええと", "えっと", "えーと",
    "あの", "あのー", "あー", "あーっと",
    "その", "そのー", "まぁ", "まあ",
    "うーん", "んー", "なんか", "えっとですね"
]


def detect_filler(
    transcript_path: Optional[str] = None,
    segments: Optional[List[Dict[str, Any]]] = None,
    custom_fillers: Optional[List[str]] = None,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Detect filler words and phrases from timestamped transcript segments."""
    fillers = custom_fillers or DEFAULT_FILLERS

    if transcript_path:
        path = Path(transcript_path)
        if not path.exists():
            raise FileNotFoundError(f"Transcript file not found: {transcript_path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            segments = data.get("segments", [])

    if segments is None:
        segments = []

    detected_items: List[Dict[str, Any]] = []

    # Regex pattern sorted by length descending
    sorted_fillers = sorted(fillers, key=len, reverse=True)
    pattern = re.compile(rf"^({'|'.join(re.escape(w) for w in sorted_fillers)})[\s、。,.・]*")

    for seg in segments:
        text = seg.get("text", "").strip()
        seg_id = seg.get("id")
        start = float(seg.get("start", 0))
        end = float(seg.get("end", 0))
        dur = max(0.1, end - start)

        # Check if entire segment is filler
        for filler in sorted_fillers:
            clean_text = re.sub(r"[、。,.・\s]", "", text)
            if clean_text == filler:
                detected_items.append({
                    "segment_id": seg_id,
                    "type": "pure_filler",
                    "matched_text": filler,
                    "full_text": text,
                    "start": start,
                    "end": end,
                    "duration": round(dur, 2),
                    "suggested_action": "remove",
                })
                break
        else:
            # Check leading filler
            m = pattern.match(text)
            if m:
                matched_word = m.group(1)
                # Estimate duration of leading filler proportional to chars
                total_len = max(1, len(text))
                filler_ratio = len(matched_word) / total_len
                est_filler_dur = min(dur * 0.5, dur * filler_ratio)
                detected_items.append({
                    "segment_id": seg_id,
                    "type": "leading_filler",
                    "matched_text": matched_word,
                    "full_text": text,
                    "start": start,
                    "end": round(start + est_filler_dur, 2),
                    "duration": round(est_filler_dur, 2),
                    "suggested_action": "trim_start",
                })

    result = {
        "count": len(detected_items),
        "fillers": detected_items,
    }

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        res = detect_filler(transcript_path=sys.argv[1])
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Usage: python -m tools.audio.filler <transcript.json>")
