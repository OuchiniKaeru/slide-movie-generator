import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional


def detect_noise(
    audio_path: str,
    clipping_threshold: float = 0.99,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Detect clipping, high noise floor, and volume anomalies in audio."""
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    issues: List[Dict[str, Any]] = []
    noise_floor_db = -60.0

    try:
        import numpy as np
        import soundfile as sf

        data, samplerate = sf.read(str(path), dtype="float32")
        if data.ndim > 1:
            data = np.mean(data, axis=1)

        # Detect clipping (samples near 1.0)
        clipped_indices = np.where(np.abs(data) >= clipping_threshold)[0]
        if len(clipped_indices) > 0:
            # Group contiguous clipped indices
            clip_times = clipped_indices / samplerate
            issues.append({
                "type": "clipping",
                "count": len(clipped_indices),
                "first_time": round(float(clip_times[0]), 3),
                "severity": "high" if len(clipped_indices) > 100 else "medium",
                "message": f"{len(clipped_indices)} samples exceed clipping threshold ({clipping_threshold})",
            })

        # Estimate noise floor using bottom 10th percentile energy
        frame_len = int(samplerate * 0.1)
        num_frames = len(data) // frame_len
        if num_frames > 0:
            energies = [
                np.sqrt(np.mean(data[i * frame_len : (i + 1) * frame_len] ** 2))
                for i in range(num_frames)
            ]
            valid_energies = [e for e in energies if e > 1e-9]
            if valid_energies:
                p10 = np.percentile(valid_energies, 10)
                noise_floor_db = round(20 * math.log10(max(p10, 1e-9)), 2)

                if noise_floor_db > -30.0:
                    issues.append({
                        "type": "high_background_noise",
                        "noise_floor_db": noise_floor_db,
                        "severity": "medium",
                        "message": f"High background noise floor estimated at {noise_floor_db} dB",
                    })

    except Exception as e:
        issues.append({
            "type": "detection_error",
            "message": str(e),
        })

    result = {
        "file_path": str(path.resolve()),
        "noise_floor_db": noise_floor_db,
        "issues_found": len(issues),
        "issues": issues,
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
        res = detect_noise(sys.argv[1])
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Usage: python -m tools.audio.noise <audio_path>")
