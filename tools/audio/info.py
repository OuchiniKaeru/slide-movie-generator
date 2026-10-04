import json
import math
import os
import subprocess
import wave
from pathlib import Path
from typing import Any, Dict


def get_audio_info(audio_path: str) -> Dict[str, Any]:
    """Get metadata and audio statistics for an audio file."""
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    ext = path.suffix.lower()
    info: Dict[str, Any] = {
        "file_name": path.name,
        "file_path": str(path.resolve()),
        "file_size": path.stat().st_size,
        "format": ext.lstrip("."),
        "sample_rate": None,
        "channels": None,
        "duration": None,
        "peak_db": None,
        "rms_db": None,
    }

    # Try soundfile first if available
    try:
        import soundfile as sf
        import numpy as np

        with sf.SoundFile(str(path)) as f:
            info["format"] = f.format
            info["subtype"] = f.subtype
            info["sample_rate"] = f.samplerate
            info["channels"] = f.channels
            info["frames"] = f.frames
            info["duration"] = round(f.frames / f.samplerate, 3)

            # Calculate volume metrics from first chunk (up to 30s) or entire file
            data = f.read(frames=min(f.frames, f.samplerate * 30), dtype="float32")
            if len(data) > 0:
                peak = float(np.max(np.abs(data)))
                rms = float(np.sqrt(np.mean(data**2)))
                info["peak_db"] = round(20 * math.log10(max(peak, 1e-9)), 2)
                info["rms_db"] = round(20 * math.log10(max(rms, 1e-9)), 2)
        return info
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback to standard library wave for WAV files
    if ext == ".wav":
        try:
            with wave.open(str(path), "rb") as wf:
                channels = wf.getnchannels()
                sample_rate = wf.getframerate()
                frames = wf.getnframes()
                sample_width = wf.getsampwidth()
                duration = round(frames / float(sample_rate), 3)

                info["channels"] = channels
                info["sample_rate"] = sample_rate
                info["sample_width_bytes"] = sample_width
                info["frames"] = frames
                info["duration"] = duration
                return info
        except Exception:
            pass

    # Fallback to ffprobe if available
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        probe_data = json.loads(res.stdout)
        format_info = probe_data.get("format", {})
        streams = probe_data.get("streams", [])
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})

        info["sample_rate"] = int(audio_stream.get("sample_rate", 0)) or None
        info["channels"] = int(audio_stream.get("channels", 0)) or None
        info["duration"] = round(float(format_info.get("duration", 0)), 3)
        info["codec_name"] = audio_stream.get("codec_name")
        info["bit_rate"] = format_info.get("bit_rate")
        return info
    except Exception:
        pass

    return info


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        print(json.dumps(get_audio_info(sys.argv[1]), indent=2, ensure_ascii=False))
    else:
        print("Usage: python -m tools.audio.info <audio_path>")
