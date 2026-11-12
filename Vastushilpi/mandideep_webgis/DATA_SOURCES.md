# Data sources

## OpenStreetMap extract

- Source: OpenStreetMap contributors via the Overpass API
- Query tool: `tools/fetch_osm.py`
- Retrieval date: 2026-11-13
- Bounding box: south 22.9938, west 77.4494, north 23.1167, east 77.5807
- Display CRS: WGS 84 / EPSG:4326
- Layers: roads, railways, waterways, waterbodies, and OSM-derived 3D flyover/pier geometry
- License: Open Database License (ODbL)
- Attribution required in the public map: “© OpenStreetMap contributors”

The GeoJSON files are stored with the static site so the deployed app does not
make live Overpass requests. Re-run the preparation script when a refreshed
OSM extract is required, review the feature counts, and redeploy.

The flyover deck and pier geometry is a display approximation generated from
`bridge=*` ways in UTM Zone 43N and exported to WGS 84. It is not engineering
survey or structural design data.
