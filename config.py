# ============================================================
# config.py  –  All settings for the SWISSIMAGE timelapse
# ============================================================

# --- Area of Interest (EPSG:2056, Swiss LV95) ---------------
# Replace these with your actual coordinates.
# Example below covers the Bern city center area.
# E (easting) runs West → East,  N (northing) runs South → North
BBOX = {
    "xmin": 2586500,   # West edge  (Easting,  EPSG:2056)
    "ymin": 1162880,   # South edge (Northing, EPSG:2056)
    "xmax": 2587600,   # East edge
    "ymax": 1163430,   # North edge
}

# --- Years to download  -------------------------------------
# Available range on SWISSIMAGE Zeitreise: 1926 – 2025
# Leave out years that have no coverage for your area.
YEARS = list(range(1970, 2026, 5))   # every 5 years: 1970, 1975, ..., 2025

# --- Image output size (pixels) -----------------------------
IMG_WIDTH  = 1024
IMG_HEIGHT = 1024

# --- Timelapse settings -------------------------------------
FPS        = 2        # frames per second in the final GIF
LOOP       = 0        # 0 = loop forever, 1 = play once

# --- File paths ---------------------------------------------
FRAMES_DIR = "frames"          # folder where downloaded JPEGs are stored
OUTPUT_GIF = "timelapse.gif"   # final output file

# --- WMTS / WMS settings (don't change unless swisstopo changes their API) ---
WMS_URL    = "https://wms.geo.admin.ch/"
LAYER      = "ch.swisstopo.swissimage-product"
CRS        = "EPSG:2056"
IMG_FORMAT = "image/jpeg"
