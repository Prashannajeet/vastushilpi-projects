# Mandideep Web GIS

This is the main Mandideep map application. It is a standalone static site based on the Mohanpura Flood Observatory architecture:

- MapLibre map shell with ArcGIS Satellite as the default basemap.
- Local versioned GeoJSON assets; no Streamlit iframe and no Python runtime required to display the map.
- Terrain, 3D buildings, 3D tree canopies/trunks, tree point marks, AOI, buffer and CAD linework as independently controlled layers.
- Lazy loading keeps the 12 MB building layer out of the initial request path until it is enabled.
- Streamlit is retained only for analysis and data preparation, not for the main user-facing map.

Run locally from this directory:

```powershell
python -m http.server 8080
```

Then open `http://localhost:8080/`. A static server is required because browsers block `fetch()` from `file://` pages.

Do not double-click `index.html`; that produces the expected `Failed to fetch` message because GeoJSON is loaded with browser `fetch()` calls.

Data display CRS is WGS 84; source/analysis CRS is EPSG:32643 / UTM Zone 43N.
