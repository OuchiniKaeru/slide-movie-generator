import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont


def asset_search(
    project_dir: str,
    query: str = "",
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """Search for existing assets in the project's assets directory."""
    assets_base = Path(project_dir) / "assets"
    results: List[Dict[str, Any]] = []

    if not assets_base.exists():
        return {"count": 0, "assets": []}

    search_dirs = [assets_base]
    if category and (assets_base / category).is_dir():
        search_dirs = [assets_base / category]

    valid_exts = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}

    for s_dir in search_dirs:
        for file in s_dir.rglob("*"):
            if file.is_file() and file.suffix.lower() in valid_exts:
                if not query or query.lower() in file.name.lower():
                    results.append({
                        "asset_id": file.stem,
                        "file_name": file.name,
                        "path": str(file.resolve()),
                        "category": file.parent.name,
                        "size_bytes": file.stat().st_size,
                    })

    return {"count": len(results), "assets": results}


def asset_generate(
    project_dir: str,
    asset_id: str,
    asset_type: str = "diagram",  # diagram, background, icon, placeholder
    text: str = "",
    width: int = 1920,
    height: int = 1080,
    bg_color: str = "#1e293b",
    fg_color: str = "#f8fafc",
    category: str = "generated",
) -> Dict[str, Any]:
    """Generate visual asset (placeholder, SVG or PNG slide/diagram/icon)."""
    out_dir = Path(project_dir) / "assets" / category
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{asset_id}.png"

    # Create image using PIL
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Basic card/frame for diagrams
    if asset_type == "diagram":
        pad = int(min(width, height) * 0.08)
        draw.rectangle(
            [pad, pad, width - pad, height - pad],
            outline=fg_color,
            width=4,
        )

    # Simple center text rendering
    display_text = text or f"Asset: {asset_id} ({asset_type})"
    draw.text((width // 2, height // 2), display_text, fill=fg_color, anchor="mm")

    img.save(str(out_path), format="PNG")

    return {
        "status": "success",
        "asset_id": asset_id,
        "type": asset_type,
        "width": width,
        "height": height,
        "file_path": str(out_path.resolve()),
    }


def asset_resize(
    input_path: str,
    output_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    maintain_aspect: bool = True,
) -> Dict[str, Any]:
    """Resize image asset with optional aspect-ratio preservation."""
    in_p = Path(input_path)
    out_p = Path(output_path)
    if not in_p.exists():
        raise FileNotFoundError(f"Asset not found: {input_path}")

    img = Image.open(str(in_p))
    orig_w, orig_h = img.size

    if width and height and maintain_aspect:
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
    elif width and height and not maintain_aspect:
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    elif width:
        ratio = width / orig_w
        img = img.resize((width, int(orig_h * ratio)), Image.Resampling.LANCZOS)
    elif height:
        ratio = height / orig_h
        img = img.resize((int(orig_w * ratio), height), Image.Resampling.LANCZOS)

    out_p.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_p))

    return {
        "status": "success",
        "original_size": [orig_w, orig_h],
        "new_size": list(img.size),
        "output_path": str(out_p.resolve()),
    }


def asset_convert(
    input_path: str,
    output_path: str,
    target_format: str = "PNG",
) -> Dict[str, Any]:
    """Convert image asset format (PNG, JPEG, WEBP, etc.)."""
    in_p = Path(input_path)
    out_p = Path(output_path)
    if not in_p.exists():
        raise FileNotFoundError(f"Asset not found: {input_path}")

    img = Image.open(str(in_p))
    if target_format.upper() in ("JPEG", "JPG") and img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    out_p.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_p), format=target_format.upper())

    return {
        "status": "success",
        "output_format": target_format.upper(),
        "output_path": str(out_p.resolve()),
    }


if __name__ == "__main__":
    import sys

    print("Asset tools module ready.")
