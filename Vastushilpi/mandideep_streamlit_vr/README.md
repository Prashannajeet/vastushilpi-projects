# Mandideep analysis dashboard

This package is the analysis companion to the main standalone Web GIS:

- `streamlit_app.py` is a lightweight inventory and analysis dashboard.
- `../mandideep_webgis/` is the main map application.
- `docs/mandideep_aoi_vr.html` remains the separate WebXR viewer.
- `data/` contains the prepared spatial layers.

## Streamlit Community Cloud

1. Push this folder to the `codex/mandideep-aoi-vr` branch of `Prashannajeet/vastushilpi-projects`.
2. In Streamlit Community Cloud, select the repository, branch, and entrypoint `streamlit_app.py`.
3. Confirm `requirements.txt` is detected.

The main Web GIS is published separately through GitHub Pages. This keeps WebGL, terrain and 3D buildings outside a Streamlit iframe.

## Local test

```powershell
python -m streamlit run streamlit_app.py
```

Set `MANDIDEEP_WEBGIS_URL` if the map is hosted at a different URL. WebXR requires HTTPS when deployed publicly.
