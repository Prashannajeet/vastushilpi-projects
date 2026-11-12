# Data contract

All bundled layers are WGS 84 display GeoJSON derived from the project source
data analyzed in EPSG:32643 / UTM Zone 43N.

| Layer | Geometry | Purpose |
|---|---|---|
| `mandideep_aoi_wgs84.geojson` | Polygon | AOI boundary |
| `mandideep_aoi_buffer_100m_wgs84.geojson` | Polygon | 100 m buffer |
| `mandideep_overture_buildings_3d_wgs84.geojson` | Polygon | 3D building footprints and display heights |
| `mandideep_tree_3d_wgs84.geojson` | Polygon | 3D tree trunk/canopy parts |
| `mandideep_tree_points_wgs84.geojson` | Point | Tree point marks |
| `aoi_tree_polygon_wgs84.geojson` | Polygon | Tree area polygon |

The app validates that every file exists and is a GeoJSON FeatureCollection
before creating the map. No local absolute Windows paths are used at runtime.

