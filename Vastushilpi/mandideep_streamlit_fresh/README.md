# Mandideep Web GIS — fresh Streamlit deployment

This is a clean, self-contained Streamlit app. It does not import the previous
Streamlit app, legacy HTML pages, CAD linework, contours, or feature-label
layers. All six active GeoJSON layers are bundled under `data/` and embedded
into one MapLibre component at runtime.

## Run locally

```powershell
cd "D:\01 Project\Development\Vastushilpi\mandideep_streamlit_fresh"
python -m streamlit run streamlit_app.py --server.port 8502
```

## Streamlit Community Cloud

- Repository: `Prashannajeet/vastushilpi-projects`
- Branch: `codex/mandideep-streamlit-fresh`
- Main file: `Vastushilpi/mandideep_streamlit_fresh/streamlit_app.py`

The map uses ArcGIS World Imagery as the default basemap. Terrain and remote
basemap tiles remain external; all project GeoJSON data is local and versioned
with this app.

