import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def scene_create(
    project_dir: str,
    scene_id: str,
    duration: float,
    background: Optional[Dict[str, Any]] = None,
    elements: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Create a new scene DSL JSON file."""
    scenes_dir = Path(project_dir) / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    scene_file = scenes_dir / f"{scene_id}.json"

    scene_data: Dict[str, Any] = {
        "scene_id": scene_id,
        "duration": duration,
        "background": background or {"type": "solid", "color": "#0f172a"},
        "elements": elements or [],
        "animations": [],
    }

    with open(scene_file, "w", encoding="utf-8") as f:
        json.dump(scene_data, f, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "scene_id": scene_id,
        "file_path": str(scene_file.resolve()),
        "scene": scene_data,
    }


def scene_read(project_dir: str, scene_id: str) -> Dict[str, Any]:
    """Read and validate a scene DSL JSON file."""
    scene_file = Path(project_dir) / "scenes" / f"{scene_id}.json"
    if not scene_file.exists():
        raise FileNotFoundError(f"Scene file not found: {scene_file}")

    with open(scene_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Basic schema validation
    required_keys = ["scene_id", "duration", "elements"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise ValueError(f"Invalid scene schema in {scene_file}: missing {missing}")

    return data


def scene_update(
    project_dir: str,
    scene_id: str,
    duration: Optional[float] = None,
    background: Optional[Dict[str, Any]] = None,
    elements_to_add: Optional[List[Dict[str, Any]]] = None,
    elements_to_remove: Optional[List[str]] = None,
    elements_to_replace: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Update elements, duration, or background of an existing scene."""
    scene_file = Path(project_dir) / "scenes" / f"{scene_id}.json"
    data = scene_read(project_dir, scene_id)

    if duration is not None:
        data["duration"] = duration
    if background is not None:
        data["background"] = background

    current_elements = data.get("elements", [])

    if elements_to_remove:
        current_elements = [el for el in current_elements if el.get("id") not in elements_to_remove]

    if elements_to_replace:
        replace_map = {el["id"]: el for el in elements_to_replace if "id" in el}
        new_elements = []
        for el in current_elements:
            el_id = el.get("id")
            if el_id in replace_map:
                new_elements.append(replace_map.pop(el_id))
            else:
                new_elements.append(el)
        # Any remaining replaces get added
        new_elements.extend(replace_map.values())
        current_elements = new_elements

    if elements_to_add:
        current_elements.extend(elements_to_add)

    data["elements"] = current_elements

    with open(scene_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "scene_id": scene_id,
        "elements_count": len(current_elements),
        "scene": data,
    }


def scene_delete(project_dir: str, scene_id: str) -> Dict[str, Any]:
    """Delete a scene JSON file."""
    scene_file = Path(project_dir) / "scenes" / f"{scene_id}.json"
    if not scene_file.exists():
        return {"status": "not_found", "scene_id": scene_id}

    scene_file.unlink()
    return {"status": "deleted", "scene_id": scene_id}


if __name__ == "__main__":
    import sys

    print("Scene tools module ready.")
