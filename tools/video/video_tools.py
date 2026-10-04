import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont


def _render_scene_image(
    scene_data: Dict[str, Any],
    width: int,
    height: int,
    output_image_path: Path,
) -> Path:
    """Render a single still frame representing a scene using PIL."""
    bg_info = scene_data.get("background", {})
    bg_color = bg_info.get("color", "#0f172a")

    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    elements = scene_data.get("elements", [])
    for el in elements:
        el_type = el.get("type")
        x = int(el.get("x", width // 2))
        y = int(el.get("y", height // 2))

        if el_type == "text":
            text = el.get("text", "")
            font_size = int(el.get("font_size", 48))
            color = el.get("color", "#f8fafc")
            draw.text((x, y), text, fill=color, anchor="mm")

        elif el_type == "image":
            asset_path = el.get("asset")
            if asset_path and Path(asset_path).exists():
                try:
                    asset_img = Image.open(asset_path).convert("RGBA")
                    # Center asset at (x, y)
                    ax = x - asset_img.width // 2
                    ay = y - asset_img.height // 2
                    img.paste(asset_img, (ax, ay), asset_img)
                except Exception:
                    pass

    output_image_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(str(output_image_path), "JPEG", quality=90)
    return output_image_path


def render_scene(
    project_dir: str,
    scene_id: str,
    output_path: Optional[str] = None,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
) -> Dict[str, Any]:
    """Render an individual scene as an MP4 clip."""
    scene_file = Path(project_dir) / "scenes" / f"{scene_id}.json"
    if not scene_file.exists():
        raise FileNotFoundError(f"Scene file not found: {scene_file}")

    with open(scene_file, "r", encoding="utf-8") as f:
        scene_data = json.load(f)

    duration = float(scene_data.get("duration", 5.0))
    temp_dir = Path(project_dir) / "render" / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    still_frame = temp_dir / f"{scene_id}_frame.jpg"
    _render_scene_image(scene_data, width, height, still_frame)

    out_mp4 = Path(output_path) if output_path else Path(project_dir) / "render" / f"{scene_id}.mp4"
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    # Use FFmpeg loop image to create clip
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(still_frame),
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        str(out_mp4),
    ]
    subprocess.run(cmd, capture_output=True, check=True)

    return {
        "status": "success",
        "scene_id": scene_id,
        "duration": duration,
        "clip_path": str(out_mp4.resolve()),
    }


def render_preview(
    project_dir: str,
    output_path: Optional[str] = None,
    width: int = 960,
    height: int = 540,
    fps: int = 24,
) -> Dict[str, Any]:
    """Generate a fast, low-resolution preview MP4 of the full video project."""
    out_file = output_path or str(Path(project_dir) / "render" / "preview.mp4")
    return render_video(
        project_dir=project_dir,
        output_path=out_file,
        width=width,
        height=height,
        fps=fps,
        is_preview=True,
    )


def render_video(
    project_dir: str,
    output_path: Optional[str] = None,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    is_preview: bool = False,
) -> Dict[str, Any]:
    """Render full project video by concatenating scenes with edited audio and subtitles."""
    p_dir = Path(project_dir)
    scenes_dir = p_dir / "scenes"
    out_file = Path(output_path) if output_path else p_dir / "render" / ("preview.mp4" if is_preview else "final.mp4")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Read storyboard to get scene order
    storyboard_file = p_dir / "storyboard" / "storyboard.json"
    scene_order = []
    if storyboard_file.exists():
        with open(storyboard_file, "r", encoding="utf-8") as f:
            sb_data = json.load(f)
            for sc in sb_data.get("scenes", []):
                scene_order.append(sc.get("id"))
    else:
        # Fallback to alphanumeric order of scene files
        scene_order = sorted([f.stem for f in scenes_dir.glob("*.json")])

    if not scene_order:
        raise ValueError(f"No scenes found in project: {project_dir}")

    # Render each scene to temporary clips
    temp_dir = p_dir / "render" / ".temp_render"
    temp_dir.mkdir(parents=True, exist_ok=True)

    rendered_clips = []
    for sc_id in scene_order:
        clip_p = temp_dir / f"{sc_id}.mp4"
        render_scene(project_dir, sc_id, str(clip_p), width=width, height=height, fps=fps)
        rendered_clips.append(clip_p)

    # Concat clips using ffmpeg concat demuxer
    concat_list = temp_dir / "concat_list.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for c in rendered_clips:
            f.write(f"file '{c.resolve().as_posix()}'\n")

    video_only = temp_dir / "video_only.mp4"
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(video_only),
    ]
    subprocess.run(cmd_concat, capture_output=True, check=True)

    # Mux with edited audio if exists
    edited_audio = p_dir / "audio" / "edited.wav"
    if not edited_audio.exists():
        edited_audio = p_dir / "audio" / "original.wav"

    final_cmd = ["ffmpeg", "-y", "-i", str(video_only)]
    if edited_audio.exists():
        final_cmd.extend(["-i", str(edited_audio)])

    # Subtitle burn-in if srt exists and not preview
    subtitles_srt = p_dir / "subtitles" / "subtitles.srt"
    if subtitles_srt.exists() and not is_preview:
        srt_escaped = str(subtitles_srt.resolve()).replace("\\", "/").replace(":", "\\:")
        final_cmd.extend(["-vf", f"subtitles='{srt_escaped}'"])

    if edited_audio.exists():
        final_cmd.extend(["-c:v", "libx264", "-c:a", "aac", "-shortest"])
    else:
        final_cmd.extend(["-c:v", "copy"])

    final_cmd.append(str(out_file))
    subprocess.run(final_cmd, capture_output=True, check=True)

    return {
        "status": "success",
        "output_file": str(out_file.resolve()),
        "is_preview": is_preview,
        "scenes_count": len(scene_order),
        "resolution": f"{width}x{height}",
        "fps": fps,
    }


def video_inspect(video_path: str) -> Dict[str, Any]:
    """Inspect video file metadata, stream information, and resolution using ffprobe."""
    v_path = Path(video_path)
    if not v_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(v_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    probe_data = json.loads(res.stdout)

    v_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "video"), {})
    a_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "audio"), {})

    return {
        "file_name": v_path.name,
        "duration": float(probe_data.get("format", {}).get("duration", 0)),
        "size_bytes": int(probe_data.get("format", {}).get("size", 0)),
        "has_video": bool(v_stream),
        "has_audio": bool(a_stream),
        "video": {
            "codec": v_stream.get("codec_name"),
            "width": v_stream.get("width"),
            "height": v_stream.get("height"),
            "fps": eval(v_stream.get("r_frame_rate", "0/1")) if "/" in v_stream.get("r_frame_rate", "") else 0,
        },
        "audio": {
            "codec": a_stream.get("codec_name"),
            "sample_rate": a_stream.get("sample_rate"),
            "channels": a_stream.get("channels"),
        } if a_stream else None,
    }


def video_extract_frame(
    video_path: str,
    time_offset: float,
    output_image_path: str,
) -> Dict[str, Any]:
    """Extract a single frame image at time_offset (seconds) for Video Critic evaluation."""
    v_path = Path(video_path)
    out_p = Path(output_image_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(time_offset),
        "-i", str(v_path),
        "-vframes", "1",
        "-q:v", "2",
        str(out_p),
    ]
    subprocess.run(cmd, capture_output=True, check=True)

    return {
        "status": "success",
        "video_path": str(v_path.resolve()),
        "time_offset": time_offset,
        "frame_image": str(out_p.resolve()),
    }


if __name__ == "__main__":
    import sys

    print("Video tools module ready.")
