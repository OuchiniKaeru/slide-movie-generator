import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional
from tools.audio.editor import concat_audio, cut_audio, normalize_audio


def render_audio_from_plan(
    original_audio_path: str,
    edit_plan_path: str,
    output_audio_path: str,
    crossfade_ms: int = 40,
    normalize: bool = True,
) -> Dict[str, Any]:
    """Execute edit_plan.json on original.wav to produce edited.wav without overwriting original.

    Supported operations:
    - remove: removes interval [start, end]
    - trim: shortens interval [start, end] to target_duration (keeps audio before/after and inserts silence or shortened gap)
    """
    orig_p = Path(original_audio_path)
    plan_p = Path(edit_plan_path)
    out_p = Path(output_audio_path)

    if not orig_p.exists():
        raise FileNotFoundError(f"Original audio not found: {original_audio_path}")
    if not plan_p.exists():
        raise FileNotFoundError(f"Edit plan not found: {edit_plan_path}")

    with open(plan_p, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    operations = plan_data.get("operations", [])
    # Sort operations by start time ascending
    sorted_ops = sorted(operations, key=lambda x: float(x.get("start", 0)))

    import soundfile as sf
    import numpy as np

    data, sr = sf.read(str(orig_p), dtype="float32")
    channels = 1 if data.ndim == 1 else data.shape[1]
    total_samples = len(data)

    # Convert remove and trim into a list of keep slices
    # Slices are tuples: (start_sample, end_sample)
    keep_chunks = []
    current_sample = 0

    for op in sorted_ops:
        op_type = op.get("type")
        op_start = max(0.0, float(op.get("start", 0)))
        op_end = min(total_samples / sr, float(op.get("end", 0)))
        start_sample = int(op_start * sr)
        end_sample = int(op_end * sr)

        if start_sample > current_sample:
            # Keep region from current_sample to start_sample
            keep_chunks.append(data[current_sample:start_sample])

        if op_type == "trim":
            # For trim (e.g. shorten silence), keep a tiny slice or insert reduced silence
            target_dur = float(op.get("target_duration", 0.2))
            trim_samples = int(target_dur * sr)
            if trim_samples > 0:
                silence_gap = np.zeros(
                    (trim_samples,) if channels == 1 else (trim_samples, channels),
                    dtype="float32",
                )
                keep_chunks.append(silence_gap)

        current_sample = max(current_sample, end_sample)

    if current_sample < total_samples:
        keep_chunks.append(data[current_sample:total_samples])

    # Assemble keep chunks with crossfade
    if not keep_chunks:
        # Fallback to copy if no slices
        keep_chunks = [data]

    cf_samples = int((crossfade_ms / 1000.0) * sr)
    assembled = keep_chunks[0]

    for nxt in keep_chunks[1:]:
        if len(nxt) == 0:
            continue
        if cf_samples > 0 and len(assembled) >= cf_samples and len(nxt) >= cf_samples:
            fade_out = np.linspace(1.0, 0.0, cf_samples)
            fade_in = np.linspace(0.0, 1.0, cf_samples)
            if channels > 1:
                fade_out = fade_out[:, np.newaxis]
                fade_in = fade_in[:, np.newaxis]

            overlap = (assembled[-cf_samples:] * fade_out) + (nxt[:cf_samples] * fade_in)
            assembled = np.concatenate([assembled[:-cf_samples], overlap, nxt[cf_samples:]], axis=0)
        else:
            assembled = np.concatenate([assembled, nxt], axis=0)

    # Peak normalization
    if normalize:
        peak = float(np.max(np.abs(assembled)))
        if peak > 1e-9:
            target_peak = 10 ** (-1.0 / 20.0)  # -1 dBFS
            assembled = assembled * (target_peak / peak)

    out_p.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_p), assembled, sr)

    duration_orig = round(total_samples / sr, 3)
    duration_edited = round(len(assembled) / sr, 3)
    duration_diff = round(duration_orig - duration_edited, 3)

    return {
        "status": "success",
        "original_audio": str(orig_p.resolve()),
        "edited_audio": str(out_p.resolve()),
        "original_duration": duration_orig,
        "edited_duration": duration_edited,
        "reduced_duration": duration_diff,
        "operations_applied": len(sorted_ops),
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 4:
        res = render_audio_from_plan(sys.argv[1], sys.argv[2], sys.argv[3])
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Usage: python -m tools.audio.renderer <orig.wav> <edit_plan.json> <edited.wav>")
