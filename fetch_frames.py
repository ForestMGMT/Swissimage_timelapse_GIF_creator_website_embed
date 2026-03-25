# ============================================================
# fetch_frames.py  –  Download one aerial image per year
#                     from the swisstopo WMS Zeitreise service
# ============================================================

import os
import urllib.request
import urllib.parse
from config import BBOX, YEARS, IMG_WIDTH, IMG_HEIGHT, FRAMES_DIR, WMS_URL, LAYER, CRS, IMG_FORMAT


def build_wms_url(year: int, bbox: dict = None, width: int = None, height: int = None) -> str:
    """
    Build a WMS 1.3.0 GetMap request URL for a given year.

    The swisstopo WMS supports a TIME parameter that selects the
    SWISSIMAGE Zeitreise snapshot for that year (e.g. TIME=1980).
    The bounding box is given in EPSG:2056 (Swiss LV95).

    WMS 1.3.0 note: BBOX order for EPSG:2056 is (South, West, North, East)
    because CRS:2056 is a geographic-ish CRS where the first axis is Northing.
    However, swisstopo's WMS accepts (West, South, East, North) regardless —
    so we use the safe (xmin, ymin, xmax, ymax) order here.
    """
    b = bbox or BBOX
    w = width  or IMG_WIDTH
    h = height or IMG_HEIGHT
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetMap",
        "LAYERS":  LAYER,
        "CRS":     CRS,
        "BBOX":    f"{b['xmin']},{b['ymin']},{b['xmax']},{b['ymax']}",
        "WIDTH":   w,
        "HEIGHT":  h,
        "FORMAT":  IMG_FORMAT,
        "STYLES":  "",
        "TIME":    str(year),
    }
    return WMS_URL + "?" + urllib.parse.urlencode(params)


def download_frame(year: int, frames_dir: str, bbox: dict = None, width: int = None, height: int = None) -> str:
    """
    Download the aerial image for *year* and save it as a JPEG.
    Returns the file path of the saved image.
    """
    os.makedirs(frames_dir, exist_ok=True)
    out_path = os.path.join(frames_dir, f"{year}.jpg")

    if os.path.exists(out_path):
        print(f"  [skip] {year}.jpg already exists")
        return out_path

    url = build_wms_url(year, bbox=bbox, width=width, height=height)
    print(f"  [download] year={year}  →  {out_path}")
    print(f"             URL: {url}")

    try:
        # Add a browser-like User-Agent header so the server doesn't block us
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()

        # Basic check: WMS error responses are XML, not JPEG
        if data[:2] == b"\xff\xd8":          # JPEG magic bytes
            with open(out_path, "wb") as f:
                f.write(data)
        else:
            # Print first 200 bytes of the response for debugging
            print(f"  [error] Unexpected response for {year}:")
            print("  ", data[:200])
            return None

    except Exception as e:
        print(f"  [error] Could not download year {year}: {e}")
        return None

    return out_path


def fetch_all_frames() -> list[str]:
    """
    Download frames for all years defined in config.py.
    Returns a sorted list of successfully downloaded file paths.
    """
    print(f"Downloading {len(YEARS)} frames into '{FRAMES_DIR}/'...")
    paths = []
    for year in sorted(YEARS):
        path = download_frame(year, FRAMES_DIR)
        if path:
            paths.append(path)
    print(f"Done. {len(paths)}/{len(YEARS)} frames downloaded.")
    return paths


if __name__ == "__main__":
    fetch_all_frames()
