# Mandideep Cesium 3D Scene

Dedicated instance name: **Mandideep Cesium 3D Scene**.

This branch is isolated from the main `Mandideep Web GIS` MapLibre application. It is the presentation-mode shell for Cesium terrain, satellite imagery, textured building meshes and 3D Tiles.

Current behavior:

- CesiumJS viewer with ArcGIS World Imagery
- Mandideep AOI camera framing
- Current merged buildings loaded as a temporary GeoJSON fallback
- Single grey building styling with dark outlines
- Reserved integration point for a photorealistic `tileset.json`

The fallback is intentionally separate from the future 3D Tiles source. Once a textured tileset is available, load it with `Cesium.Cesium3DTileset.fromUrl()` and remove or disable the fallback layer.
