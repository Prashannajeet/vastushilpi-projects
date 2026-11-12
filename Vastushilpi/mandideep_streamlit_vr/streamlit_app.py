from __future__ import annotations

from pathlib import Path

import streamlit as st


# Deployment marker: forces Community Cloud to rebuild the static-file map shell.
APP_BUILD = "mandideep-static-map-2026-11-12"


st.set_page_config(page_title="Mandideep Web GIS", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
    <style>
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main { height: 100vh !important; min-height: 100vh !important; }
    [data-testid="stAppViewContainer"] > .main { padding: 0 !important; overflow: hidden !important; }
    [data-testid="stMainBlockContainer"], .block-container { max-width: none !important; width: 100% !important; padding: 0 !important; margin: 0 !important; }
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none; }
    [data-testid="stVerticalBlock"] { gap: 0 !important; }
    iframe { border: 0 !important; display: block; width: 100% !important; height: 100vh !important; min-height: 100vh !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# The deployment uses a self-contained local HTML file. This avoids relying on
# Streamlit Cloud's static-file route, which is unavailable in this app.
MAP_FILE = Path(__file__).resolve().parent / "static" / "mandideep_embedded_map.html"
st.iframe(
    MAP_FILE,
    height=1000,
)
