# ============================================================
# main.py  –  Run the full SWISSIMAGE timelapse pipeline
#
# Usage:
#   python main.py
#
# Steps:
#   1. Read settings from config.py
#   2. Download one aerial image per year via swisstopo WMS
#   3. Assemble all frames into an animated GIF
# ============================================================

from fetch_frames import fetch_all_frames
from make_timelapse import make_gif
from config import OUTPUT_GIF, FPS, LOOP, FRAMES_DIR
import os


def main():
    print("=" * 60)
    print("  SWISSIMAGE Timelapse Generator")
    print("=" * 60)

    # Step 1: Download frames
    print("\n[ Step 1/2 ]  Downloading frames from swisstopo WMS...\n")
    frame_paths = fetch_all_frames()

    if not frame_paths:
        print("\n[abort] No frames were downloaded. Check your bbox and years in config.py.")
        return

    # Step 2: Build GIF
    print(f"\n[ Step 2/2 ]  Assembling {len(frame_paths)} frames into GIF...\n")
    make_gif(frame_paths, OUTPUT_GIF, fps=FPS, loop=LOOP)

    print("\nDone! Open", os.path.abspath(OUTPUT_GIF), "to view the timelapse.")


if __name__ == "__main__":
    main()
