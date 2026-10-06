# Vastushilpi Projects

A Streamlit GIS application for the Grid survey (2009) and Hiraundi I–A survey, with satellite imagery by default, topographic basemaps, smooth DEM/hillshade layers, contours, editable map drawings and elevation profiles.

## Run locally

Double-click **Start Vastushilpi Projects.command** on this Mac, or use Python 3.12:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open http://127.0.0.1:8501. Keep the server running while using the app.

## Use the maps

Select a survey in the sidebar. Choose Satellite imagery or Topography; toggle terrain layers and adjust DEM opacity. The map toolbar draws lines, polygons, rectangles and markers and edits/deletes them. Draw a line and click its last vertex again (or Finish) to create a profile. Select among multiple drawn lines below the map. Download drawings as WGS84 GeoJSON and profiles as CSV with native projected coordinates.

Drawings belong to the browser session. Export before closing or refreshing. Separate surveys keep separate session state. The GeoJSON contains user annotations, not legally surveyed boundaries. Online basemaps and Folium's map libraries require internet access.

## Data and coordinate systems

The app reuses existing files without duplicating them:

- `Interactive_Maps/assets/`: georeferenced display images, coverage masks, contours and survey configuration.
- `outputs/grid_dem_0p5m.tif`: original 0.5 m TIN DEM, EPSG:32643, WGS84 / UTM43N.
- `outputs/geolocation_dem_0p5m.tif`: original 0.5 m TIN DEM, EPSG:24379, Kalianpur1975 / IndiaIIa.

Set `VASTUSHILPI_DATA_DIR` to another DEM directory if needed. The viewer still works when rasters are missing, but elevation profiles require the original DEM. An upload control accepts a projected DEM with the correct EPSG; users must ensure it is the intended original survey surface. Uploaded rasters are used in memory for the session and are not written into the project.

Profiles use bilinear sampling of original raster cells and native projected distance. Samples are spaced at up to 0.5 m for ordinary routes, capped at 20,001 samples and 100 km total route length. NoData gaps remain blank. The display images are downsampled Web Mercator overlays; the original rasters preserve their native CRS and cell size.

The smooth display uses Gaussian sigma 1 m and the hillshade averages four light azimuths. These derivatives are not EBK or independently validated replacement terrain. Source point spacing is 5 m / 10 m; 0.5 m cells do not imply 0.5 m accuracy. Hiraundi placement comes from CAD GEODATA, with a Kalianpur→WGS84 operation of stated 22 m accuracy; satellite alignment is unverified. Vertical datum remains unconfirmed for both surveys.

## Git and deployment

This folder is the local Git repository for **Vastushilpi Projects**. The source, compact web assets and pinned dependencies are versioned. CAD files, remaining GIS outputs, virtual environments, exports and secrets are excluded by `.gitignore`. The two original DEM GeoTIFFs and projection/world-file sidecars are included for hosted elevation profiles.

GitHub repository: https://github.com/Prashannajeet/vastushilpi-projects (private).

Streamlit Community Cloud deployment: repository `Prashannajeet/vastushilpi-projects`, branch `main`, entrypoint `streamlit_app.py`, Python **3.12** under Advanced settings. The original DEMs are included. Deployment requires the owner to sign into Streamlit and accept its hosting terms. Live app: https://vastushilpi-projects.streamlit.app/

Successfully deployed on Streamlit Community Cloud with Python 3.12.15. App sharing remains private (sign-in/invitation required). Both native DEMs are available on the hosted server; a 678.8 m Grid test route returned 100% DEM support at 0.50 m intervals.

The hosting configuration binds to `0.0.0.0`; the Mac launcher explicitly binds local runs to `127.0.0.1`. Do not publish `.streamlit/secrets.toml`.

## Validation

```sh
python -m unittest discover -s tests -v
```

Tests verify a known planar surface, projected route distances, NoData gaps, outside-raster routes and zero-length rejection. Streamlit AppTest checks both surveys and topographic selection. Browser checks cover actual map rendering, drawn routes and profile charts.

## Attribution and documentation

Imagery: Esri, Maxar, Earthstar Geographics and GIS User Community. Topography: OpenStreetMap contributors/SRTM; OpenTopoMap style CC-BY-SA. Attribution remains visible on the map.

- [Streamlit installation](https://docs.streamlit.io/get-started/installation)
- [Streamlit dependencies for deployment](https://docs.streamlit.io/deploy/concepts/dependencies)
- [streamlit-folium](https://github.com/randyzwitch/streamlit-folium)
- [Rasterio windowed reading](https://rasterio.readthedocs.io/en/latest/topics/windowed-rw.html)
- [Esri attribution](https://support.esri.com/en-us/knowledge-base/what-is-the-correct-way-to-cite-an-arcgis-online-basema-000012040)
- [OpenTopoMap](https://opentopomap.org/about)
