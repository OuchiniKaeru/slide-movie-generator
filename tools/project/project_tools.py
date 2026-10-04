import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

SUBDIRECTORIES = [
    "input",
    "analysis",
    "transcript",
    "audio",
    "editing",
    "storyboard",
    "scenes",
    "assets/images",
    "assets/icons",
    "assets/diagrams",
    "assets/generated",
    "subtitles",
    "render",
    "review",
]

VALID_STAGES = [
    "created",
    "analyzing",
    "editing_audio",
    "reviewing_audio",
    "planning",
    "designing",
    "rendering",
    "reviewing_video",
    "completed",
    "failed",
]


def project_init(
    project_dir: str,
    project_id: Optional[str] = None,
    source_audio: Optional[str] = None,
) -> Dict[str, Any]:
    """Initialize a video project directory structure according to specification section 5."""
    p_path = Path(project_dir)
    p_path.mkdir(parents=True, exist_ok=True)
    proj_id = project_id or p_path.name

    for sub in SUBDIRECTORIES:
        (p_path / sub).mkdir(parents=True, exist_ok=True)

    input_audio_rel = None
    if source_audio:
        src = Path(source_audio)
        if src.exists():
            dest = p_path / "input" / src.name
            shutil.copy(str(src), str(dest))
            # Also keep original in audio/original.wav
            orig_dest = p_path / "audio" / "original.wav"
            shutil.copy(str(src), str(orig_dest))
            input_audio_rel = f"input/{src.name}"

    project_data = {
        "project_id": proj_id,
        "status": "created",
        "current_stage": "created",
        "source_audio": input_audio_rel,
        "edited_audio": None,
        "final_video": None,
        "config": {
            "audio_editing": {
                "silence": {"enabled": True, "min_duration": 0.8, "keep_duration": 0.2},
                "filler": {"enabled": True},
                "repetition": {"enabled": True},
                "self_correction": {"enabled": True},
                "noise_reduction": {"enabled": True},
                "normalization": {"enabled": True},
            },
            "video": {
                "resolution": "1920x1080",
                "fps": 30,
                "format": "mp4",
            },
            "subtitle": {"enabled": True},
            "animation": {"level": "medium"},
        },
    }

    proj_file = p_path / "project.json"
    with open(proj_file, "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "project_id": proj_id,
        "project_dir": str(p_path.resolve()),
        "project_file": str(proj_file.resolve()),
        "project_data": project_data,
    }


def project_status(project_dir: str) -> Dict[str, Any]:
    """Get the current state and file availability of a project."""
    p_path = Path(project_dir)
    proj_file = p_path / "project.json"
    if not proj_file.exists():
        raise FileNotFoundError(f"Project configuration not found: {proj_file}")

    with open(proj_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check key intermediate files
    data["files_exist"] = {
        "input_audio": (p_path / "input").exists() and any((p_path / "input").iterdir()),
        "audio_info": (p_path / "analysis" / "audio_info.json").exists(),
        "transcript_original": (p_path / "transcript" / "original.json").exists(),
        "transcript_edited": (p_path / "transcript" / "edited.json").exists(),
        "audio_original": (p_path / "audio" / "original.wav").exists(),
        "audio_edited": (p_path / "audio" / "edited.wav").exists(),
        "edit_plan": (p_path / "editing" / "edit_plan.json").exists(),
        "storyboard": (p_path / "storyboard" / "storyboard.json").exists(),
        "scenes_count": len(list((p_path / "scenes").glob("*.json"))),
        "subtitles_srt": (p_path / "subtitles" / "subtitles.srt").exists(),
        "preview_video": (p_path / "render" / "preview.mp4").exists(),
        "final_video": (p_path / "render" / "final.mp4").exists(),
    }

    return data


def project_update_stage(
    project_dir: str,
    stage: str,
    status: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Update current stage and status in project.json."""
    if stage not in VALID_STAGES:
        raise ValueError(f"Invalid stage '{stage}'. Must be one of: {VALID_STAGES}")

    p_path = Path(project_dir)
    proj_file = p_path / "project.json"
    if not proj_file.exists():
        raise FileNotFoundError(f"Project configuration not found: {proj_file}")

    with open(proj_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["current_stage"] = stage
    data["status"] = status or stage

    if extra_fields:
        data.update(extra_fields)

    with open(proj_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return data


if __name__ == "__main__":
    import sys

    print("Project tools module ready.")
