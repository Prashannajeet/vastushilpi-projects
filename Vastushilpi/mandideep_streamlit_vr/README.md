# Mandideep AOI Streamlit + VR

This package separates the GIS dashboard from the immersive viewer:

- `streamlit_app.py` is the Streamlit data dashboard.
- `docs/mandideep_aoi_vr.html` is the standalone WebXR viewer.
- `data/` contains the prepared spatial layers used by both viewers.

## Streamlit Community Cloud

1. Push this folder to the `codex/mandideep-aoi-vr` branch.
2. In Streamlit Community Cloud, select the repository, branch, and entrypoint `streamlit_app.py`.
3. Confirm `requirements.txt` is detected.

The standalone VR page should be published through GitHub Pages from the `docs/` folder. This keeps WebXR outside a Streamlit iframe, which is important for headset permissions.

## Local test

```powershell
python -m streamlit run streamlit_app.py
python -m http.server 8765 --directory docs
```

WebXR requires HTTPS when deployed publicly. GitHub Pages provides HTTPS automatically.
