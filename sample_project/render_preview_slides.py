import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
    "C:/Windows/Fonts/YuGothM.ttc",
    "C:/Windows/Fonts/arial.ttf",
]

def get_font(size: int):
    for f in FONT_CANDIDATES:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                continue
    return ImageFont.load_default()

def render_preview_slide(scene_json_path: Path, output_png_path: Path, width=1920, height=1080):
    with open(scene_json_path, "r", encoding="utf-8") as f:
        scene = json.load(f)

    bg_info = scene.get("background", {})
    bg_color = bg_info.get("color", "#0b0f19")
    if bg_info.get("type") == "gradient":
        bg_color = bg_info.get("colors", ["#060913"])[0]

    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Accent top border
    draw.rectangle([0, 0, width, 6], fill="#38bdf8")

    elements = scene.get("elements", [])
    for el in elements:
        el_type = el.get("type")
        x = int(el.get("x", width // 2))
        y = int(el.get("y", height // 2))

        if el_type in ("text", "typewriter_text", "badge"):
            text = el.get("text", "")
            size = int(el.get("font_size", 32))
            color = el.get("color", "#ffffff")
            font = get_font(size)
            
            lines = text.split("\n")
            line_spacing = int(size * 1.35)
            total_h = len(lines) * line_spacing
            start_y = y - total_h // 2

            for i, line in enumerate(lines):
                ly = start_y + i * line_spacing
                draw.text((x, ly), line, fill=color, font=font, anchor="mm")

        elif el_type == "card":
            w = int(el.get("width", 420))
            h = int(el.get("height", 380))
            accent = el.get("accent_color", "#38bdf8")
            
            # Card background
            card_rect = [x - w // 2, y - h // 2, x + w // 2, y + h // 2]
            draw.rectangle(card_rect, fill="#0f172a", outline="#334155", width=2)
            # Top accent bar on card
            draw.rectangle([card_rect[0], card_rect[1], card_rect[2], card_rect[1] + 4], fill=accent)

            # Metric Value
            val = el.get("metric_value", "")
            if val:
                font_val = get_font(52)
                draw.text((x, y - 80), val, fill=accent, font=font_val, anchor="mm")

            # Metric Label
            lbl = el.get("metric_label", "")
            if lbl:
                font_lbl = get_font(24)
                draw.text((x, y - 10), lbl, fill="#f8fafc", font=font_lbl, anchor="mm")

            # Description
            desc = el.get("description", "")
            if desc:
                font_desc = get_font(18)
                lines = desc.split("\n")
                for i, l in enumerate(lines):
                    draw.text((x, y + 60 + i * 26), l, fill="#94a3b8", font=font_desc, anchor="mm")

    output_png_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(str(output_png_path), "PNG")
    print(f"Rendered: {output_png_path}")

def main():
    scenes_dir = Path("sample_project/scenes")
    out_dir = Path("sample_project/preview_slides")
    for f in sorted(scenes_dir.glob("*.json")):
        out_png = out_dir / f"{f.stem}.png"
        render_preview_slide(f, out_png)

if __name__ == "__main__":
    main()
