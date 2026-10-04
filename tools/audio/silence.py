import json
import math
import subprocess
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional


def detect_silence(
    audio_path: str,
    min_duration: float = 0.8,
    silence_threshold_db: float = -40.0,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Detect silence segments in an audio file.

    Returns:
        Dict with 'silence_segments': [{'start': float, 'end': float, 'duration': float}]
    """
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    silence_segments: List[Dict[str, float]] = []

    # 1. Try numpy/soundfile
    try:
        import numpy as np
        import soundfile as sf

        data, samplerate = sf.read(str(path), dtype="float32")
        if data.ndim > 1:
            data = np.mean(data, axis=1)  # mono

        # Frame based energy calculation (frame size 50ms)
        frame_len = int(samplerate * 0.05)
        hop_len = int(samplerate * 0.025)
        num_frames = (len(data) - frame_len) // hop_len

        threshold_amp = 10 ** (silence_threshold_db / 20)

        in_silence = False
        silence_start = 0.0

        for i in range(num_frames):
            frame = data[i * hop_len : i * hop_len + frame_len]
            rms = np.sqrt(np.mean(frame**2))
            t = (i * hop_len) / samplerate

            if rms < threshold_amp:
                if not in_silence:
                    in_silence = True
                    silence_start = t
            else:
                if in_silence:
                    in_silence = False
                    dur = t - silence_start
                    if dur >= min_duration:
                        silence_segments.append({
                            "start": round(silence_start, 3),
                            "end": round(t, 3),
                            "duration": round(dur, 3),
                        })

        if in_silence:
            total_dur = len(data) / samplerate
            dur = total_dur - silence_start
            if dur >= min_duration:
                silence_segments.append({
                    "start": round(silence_start, 3),
                    "end": round(total_dur, 3),
                    "duration": round(dur, 3),
                })

    except Exception:
        # 2. Fallback to FFmpeg silencedetect
        try:
            cmd = [
                "ffmpeg",
                "-i", str(path),
                "-af", f"silencedetect=noise={silence_threshold_db}dB:d={min_duration}",
                "-f", "null",
                "-",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            import re

            starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9\.]+)", res.stderr)]
            ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9\.]+)", res.stderr)]

            for s, e in zip(starts, ends):
                silence_segments.append({
                    "start": round(s, 3),
                    "end": round(e, 3),
                    "duration": round(e - s, 3),
                })
        except Exception:
            pass

    result = {
        "file_path": str(path.resolve()),
        "min_duration": min_duration,
        "silence_threshold_db": silence_threshold_db,
        "count": len(silence_segments),
        "silence_segments": silence_segments,
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
        res = detect_silence(sys.argv[1])
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Usage: python -m tools.audio.silence <audio_path>")
