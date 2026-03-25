# ============================================================
# make_timelapse.py  –  Assemble downloaded frames into a GIF
#
# Core logic adapted from:
#   github.com/opengeos/qgis-timelapse-plugin
#   timelapse/core/timelapse_core.py  →  make_gif() / add_text_to_gif()
# ============================================================

import os
import re
from PIL import Image, ImageDraw, ImageFont
from config import FPS, LOOP, OUTPUT_GIF, FRAMES_DIR


def extract_year(filepath: str) -> str:
    """Parse the year from a filename like 'frames/1980.jpg' → '1980'."""
    name = os.path.basename(filepath)
    match = re.search(r"(\d{4})", name)
    return match.group(1) if match else ""


def add_year_label(image: Image.Image, year: str) -> Image.Image:
    """
    Burn the year as white text in the top-left corner of the frame.
    Falls back to the default PIL font if a nicer one isn't available.
    Adapted from timelapse_core.py → add_text_to_gif()
    """
    frame = image.convert("RGBA")
    draw  = ImageDraw.Draw(frame)

    # Try to load a readable font; fall back to PIL default if not found
    try:
        font = ImageFont.truetype("arial.ttf", size=48)
    except IOError:
        font = ImageFont.load_default()

    x = int(frame.width  * 0.02)   # 2% from left
    y = int(frame.height * 0.02)   # 2% from top

    # Draw a dark shadow first so the text is readable on any background
    draw.text((x + 2, y + 2), year, font=font, fill=(0, 0, 0, 200))
    draw.text((x,     y    ), year, font=font, fill=(255, 255, 255, 255))

    return frame.convert("RGB")


def make_gif(image_paths: list[str], out_gif: str, fps: int = 2, loop: int = 0) -> None:
    """
    Create an animated GIF from a list of JPEG file paths.

    Parameters
    ----------
    image_paths : sorted list of JPEG file paths (one per year)
    out_gif     : output path for the GIF (e.g. 'timelapse.gif')
    fps         : frames per second  (duration per frame = 1000/fps ms)
    loop        : 0 = loop forever,  1 = play once

    Adapted from timelapse_core.py → make_gif()
    """
    if not image_paths:
        print("[error] No frames to assemble.")
        return

    frames = []
    for path in image_paths:
        year  = extract_year(path)
        img   = Image.open(path)
        frame = add_year_label(img, year)
        frames.append(frame)
        print(f"  [frame] {year}  ({img.width}×{img.height}px)")

    duration_ms = int(1000 / fps)

    frames[0].save(
        out_gif,
        format="GIF",
        append_images=frames[1:],
        save_all=True,
        duration=duration_ms,
        loop=loop,
        optimize=False,      # keep full colour fidelity
    )
    print(f"\nGIF saved → {out_gif}  ({len(frames)} frames, {fps} fps)")


if __name__ == "__main__":
    # Collect all JPEGs from the frames folder, sorted by year
    frame_files = sorted(
        [os.path.join(FRAMES_DIR, f) for f in os.listdir(FRAMES_DIR) if f.endswith(".jpg")]
    )
    if not frame_files:
        print(f"No frames found in '{FRAMES_DIR}/'. Run fetch_frames.py first.")
    else:
        make_gif(frame_files, OUTPUT_GIF, fps=FPS, loop=LOOP)
