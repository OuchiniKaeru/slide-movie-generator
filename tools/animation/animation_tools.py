import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from tools.scene.scene_tools import scene_read


VALID_ANIMATION_TYPES = {
    "fade_in", "fade_out", "move", "scale", "rotate",
    "slide", "reveal", "typewriter", "emphasis", "highlight",
    "morph", "transition"
}


def animation_add(
    project_dir: str,
    scene_id: str,
    element_id: str,
    animation_type: str,
    start_time: float,
    duration: float,
    easing: str = "ease_out",
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Add an animation effect to an element in a scene."""
    scene_file = Path(project_dir) / "scenes" / f"{scene_id}.json"
    data = scene_read(project_dir, scene_id)

    # Validate element exists
    elem_ids = [el.get("id") for el in data.get("elements", [])]
    if element_id not in elem_ids and element_id != "scene":
        raise ValueError(f"Element ID '{element_id}' not found in scene '{scene_id}'")

    if "animations" not in data:
        data["animations"] = []

    anim_id = f"anim_{len(data['animations']) + 1:03d}"
    anim_entry = {
        "id": anim_id,
        "element_id": element_id,
        "type": animation_type,
        "start": start_time,
        "duration": duration,
        "easing": easing,
        "parameters": parameters or {},
    }

    data["animations"].append(anim_entry)

    with open(scene_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "scene_id": scene_id,
        "animation": anim_entry,
    }


def animation_update(
    project_dir: str,
    scene_id: str,
    animation_id: str,
    animation_type: Optional[str] = None,
    start_time: Optional[float] = None,
    duration: Optional[float] = None,
    easing: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Update properties of an existing animation in a scene."""
    scene_file = Path(project_dir) / "scenes" / f"{scene_id}.json"
    data = scene_read(project_dir, scene_id)

    animations = data.get("animations", [])
    target = next((a for a in animations if a.get("id") == animation_id), None)
    if not target:
        raise ValueError(f"Animation ID '{animation_id}' not found in scene '{scene_id}'")

    if animation_type is not None:
        target["type"] = animation_type
    if start_time is not None:
        target["start"] = start_time
    if duration is not None:
        target["duration"] = duration
    if easing is not None:
        target["easing"] = easing
    if parameters is not None:
        target["parameters"].update(parameters)

    with open(scene_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "scene_id": scene_id,
        "animation": target,
    }


def animation_delete(
    project_dir: str,
    scene_id: str,
    animation_id: str,
) -> Dict[str, Any]:
    """Delete an animation from a scene."""
    scene_file = Path(project_dir) / "scenes" / f"{scene_id}.json"
    data = scene_read(project_dir, scene_id)

    orig_count = len(data.get("animations", []))
    data["animations"] = [a for a in data.get("animations", []) if a.get("id") != animation_id]

    with open(scene_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "scene_id": scene_id,
        "removed": orig_count != len(data["animations"]),
    }


if __name__ == "__main__":
    import sys

    print("Animation tools module ready.")
