# Mandideep 3D GIS · Cesium

Separate presentation instance for the Mandideep project. The main MapLibre app is not modified by this instance.

## Included layers

- ArcGIS World Imagery plus OpenStreetMap fallback imagery
- AOI and 100 m buffer
- 24,161 merged 3D building footprints with bounded 6–60 m extrusion and grey facade styling
- 978 3D tree canopy/trunk polygons with 5–30 m extrusion
- 607 roads, 54 railways, 9 waterways, 8 waterbodies
- 346 flyover / bridge-pier polygons with height attributes
- Modeled roadside trees, electric poles and overhead wires generated from the road centerlines for visual context; these are not surveyed utility assets
- Layer-by-layer visibility controls and isolated error handling

All web paths are relative to `data/`; no Windows paths are referenced by the deployed app.

## 3D-GloBFP source status

The local repository contains tile 1821 (`77.5–78.75°E`, `22.5–23.75°N`) as an ESRI Shapefile archive. It covers Mandideep, but it is not a ready Cesium 3D Tiles package. No Mandideep `tileset.json` was found, so the deployment uses the validated clipped/merged GeoJSON derivative and records the source in `data/tile-source-manifest.json`. This prevents an unverified or broken tileset from taking down the scene.

## Local run

From this directory:

```powershell
python -m http.server 8090
```

Then open `http://localhost:8090/`. The app must be served over HTTP because browsers block local GeoJSON requests from `file://` pages.
