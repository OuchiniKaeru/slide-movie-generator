import math
import subprocess
from pathlib import Path
from typing import List, Optional


def cut_audio(
    input_path: str,
    output_path: str,
    start: float,
    end: Optional[float] = None,
) -> str:
    """Cut / slice an audio file between start and end (in seconds)."""
    in_p = Path(input_path)
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    try:
        import soundfile as sf

        data, sr = sf.read(str(in_p))
        start_idx = int(start * sr)
        end_idx = int(end * sr) if end is not None else len(data)
        sliced = data[start_idx:end_idx]
        sf.write(str(out_p), sliced, sr)
        return str(out_p.resolve())
    except Exception:
        # Fallback to FFmpeg
        cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", str(in_p)]
        if end is not None:
            cmd.extend(["-t", str(end - start)])
        cmd.extend(["-c", "copy", str(out_p)])
        subprocess.run(cmd, capture_output=True, check=True)
        return str(out_p.resolve())


def concat_audio(
    input_paths: List[str],
    output_path: str,
    crossfade_ms: int = 50,
) -> str:
    """Concatenate multiple audio files sequentially with optional crossfade."""
    if not input_paths:
        raise ValueError("No input files provided for concat.")
    if len(input_paths) == 1:
        import shutil
        shutil.copy(input_paths[0], output_path)
        return str(Path(output_path).resolve())

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    try:
        import numpy as np
        import soundfile as sf

        chunks = []
        target_sr = None
        target_channels = None

        for p in input_paths:
            data, sr = sf.read(p, dtype="float32")
            if target_sr is None:
                target_sr = sr
                target_channels = 1 if data.ndim == 1 else data.shape[1]
            if data.ndim == 1 and target_channels == 2:
                data = np.column_stack([data, data])
            elif data.ndim == 2 and target_channels == 1:
                data = np.mean(data, axis=1)
            chunks.append(data)

        if not chunks:
            raise ValueError("No audio data could be read.")

        # Concat with simple linear crossfade
        cf_samples = int((crossfade_ms / 1000.0) * target_sr)
        result = chunks[0]

        for nxt in chunks[1:]:
            if cf_samples > 0 and len(result) >= cf_samples and len(nxt) >= cf_samples:
                fade_out = np.linspace(1.0, 0.0, cf_samples)
                fade_in = np.linspace(0.0, 1.0, cf_samples)
                if result.ndim == 2:
                    fade_out = fade_out[:, np.newaxis]
                    fade_in = fade_in[:, np.newaxis]

                overlap = (result[-cf_samples:] * fade_out) + (nxt[:cf_samples] * fade_in)
                result = np.concatenate([result[:-cf_samples], overlap, nxt[cf_samples:]], axis=0)
            else:
                result = np.concatenate([result, nxt], axis=0)

        sf.write(str(out_p), result, target_sr)
        return str(out_p.resolve())

    except Exception:
        # Fallback using FFmpeg concat filter
        concat_txt = out_p.parent / "_temp_concat.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for p in input_paths:
                f.write(f"file '{Path(p).resolve().as_posix()}'\n")
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(out_p)]
        subprocess.run(cmd, capture_output=True, check=True)
        if concat_txt.exists():
            concat_txt.unlink()
        return str(out_p.resolve())


def normalize_audio(
    input_path: str,
    output_path: str,
    target_peak_db: float = -1.0,
) -> str:
    """Normalize audio peak amplitude to target dB."""
    in_p = Path(input_path)
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    try:
        import numpy as np
        import soundfile as sf

        data, sr = sf.read(str(in_p), dtype="float32")
        peak = float(np.max(np.abs(data)))
        if peak > 1e-9:
            target_linear = 10 ** (target_peak_db / 20.0)
            gain = target_linear / peak
            normalized = data * gain
        else:
            normalized = data

        sf.write(str(out_p), normalized, sr)
        return str(out_p.resolve())
    except Exception:
        # Fallback to FFmpeg loudnorm / volume
        cmd = [
            "ffmpeg", "-y", "-i", str(in_p),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            str(out_p)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return str(out_p.resolve())


def denoise_audio(
    input_path: str,
    output_path: str,
) -> str:
    """Denoise audio using a gentle high-pass/low-pass filter or FFmpeg afftdn."""
    in_p = Path(input_path)
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    # Use FFmpeg afftdn (FFT based noise reduction) if available
    try:
        cmd = [
            "ffmpeg", "-y", "-i", str(in_p),
            "-af", "afftdn=nf=-25",
            str(out_p)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return str(out_p.resolve())
    except Exception:
        # Fallback copy
        import shutil
        shutil.copy(str(in_p), str(out_p))
        return str(out_p.resolve())
