# ============================================================
# app.py  –  Streamlit GUI for the SWISSIMAGE Timelapse Generator
#
# Run with:
#   python -m streamlit run app.py
# ============================================================

import os
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
from pyproj import Transformer
import streamlit as st
from fetch_frames import download_frame
from make_timelapse import make_gif

st.set_page_config(page_title="SWISSIMAGE Timelapse", layout="wide")
st.title("SWISSIMAGE Timelapse Generator")
st.markdown("Draw your area of interest on the map, set a year range, and generate an animated GIF.")

# ── Step 1: Interactive map ───────────────────────────────────────────────────
st.subheader("Step 1 — Draw your bounding box")
st.caption("Use the rectangle tool (□) on the left side of the map. Draw one rectangle — it will be used as the area of interest.")

# Centre on Switzerland
m = folium.Map(location=[46.8, 8.2], zoom_start=8, tiles=None)

# swisstopo SWISSIMAGE as base layer (Web Mercator tiles, no API key needed)
folium.TileLayer(
    tiles="https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg",
    attr="© swisstopo",
    name="SWISSIMAGE (current)",
    max_zoom=19,
).add_to(m)

# Draw plugin — rectangles only
Draw(
    export=False,
    draw_options={
        "rectangle":    True,
        "polygon":      False,
        "circle":       False,
        "marker":       False,
        "polyline":     False,
        "circlemarker": False,
    },
    edit_options={"edit": False, "remove": True},
).add_to(m)

map_result = st_folium(m, width="100%", height=520, returned_objects=["all_drawings"])

# Convert drawn rectangle from WGS84 → EPSG:2056
bbox_2056 = None
if map_result and map_result.get("all_drawings"):
    drawings = map_result["all_drawings"]
    if drawings:
        # Use the most recently drawn shape
        coords = drawings[-1]["geometry"]["coordinates"][0]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]

        transformer = Transformer.from_crs("EPSG:4326", "EPSG:2056", always_xy=True)
        xmin, ymin = transformer.transform(min(lons), min(lats))
        xmax, ymax = transformer.transform(max(lons), max(lats))
        bbox_2056 = {
            "xmin": int(xmin), "ymin": int(ymin),
            "xmax": int(xmax), "ymax": int(ymax),
        }
        st.success(
            f"Bounding box captured (EPSG:2056) — "
            f"xmin: {bbox_2056['xmin']}  ymin: {bbox_2056['ymin']}  "
            f"xmax: {bbox_2056['xmax']}  ymax: {bbox_2056['ymax']}"
        )
else:
    st.info("No bounding box drawn yet. Use the rectangle tool on the map above.")

# ── Step 2: Settings ─────────────────────────────────────────────────────────
st.subheader("Step 2 — Settings")

col1, col2, col3 = st.columns(3)
with col1:
    project_name = st.text_input("Project name", placeholder="e.g. Bern_Altstadt")
with col2:
    year_start = st.number_input("From year", min_value=1926, max_value=2025, value=1970, step=1)
    year_end   = st.number_input("To year",   min_value=1926, max_value=2025, value=2025, step=1)
with col3:
    step = st.selectbox("Step (every N years)", options=[1, 2, 5, 10], index=2)
    fps  = st.slider("Frames per second", min_value=1, max_value=10, value=2)
    size = st.selectbox("Image size (pixels)", options=[512, 1024, 2048], index=1)

# ── Step 3: Run ───────────────────────────────────────────────────────────────
st.subheader("Step 3 — Generate")

if st.button("Run", type="primary"):

    # Validation
    if not project_name.strip():
        st.error("Please enter a project name.")
        st.stop()
    if bbox_2056 is None:
        st.error("Please draw a bounding box on the map first.")
        st.stop()
    if year_start >= year_end:
        st.error("Start year must be before end year.")
        st.stop()

    years      = list(range(int(year_start), int(year_end) + 1, step))
    frames_dir = os.path.join("frames", project_name.strip())
    out_gif    = f"{project_name.strip()}_timelapse.gif"

    st.info(f"Downloading {len(years)} frames ({year_start} → {year_end}, every {step} year(s))...")
    progress_bar = st.progress(0)
    status_text  = st.empty()

    downloaded = []
    for i, year in enumerate(years):
        status_text.text(f"Fetching {year}...")
        path = download_frame(year, frames_dir, bbox=bbox_2056, width=size, height=size)
        if path:
            downloaded.append(path)
        progress_bar.progress((i + 1) / len(years))

    if not downloaded:
        st.error("No frames could be downloaded. Try a different area or year range.")
        st.stop()

    status_text.text(f"Assembling {len(downloaded)} frames into GIF...")
    make_gif(downloaded, out_gif, fps=fps, loop=0)
    status_text.text("Done!")

    st.success(f"Timelapse ready — {len(downloaded)} frames at {fps} fps")

    with open(out_gif, "rb") as f:
        gif_bytes = f.read()

    st.download_button(
        label="⬇ Download timelapse GIF",
        data=gif_bytes,
        file_name=out_gif,
        mime="image/gif",
    )

    st.image(gif_bytes, caption=f"{project_name} · {year_start}–{year_end}")
