# Data preparation tools

Run from the `mandideep_webgis` directory:

```powershell
python tools/fetch_osm.py
```

The script queries OpenStreetMap's Overpass API for the project bounding box,
then writes five versioned WGS 84 GeoJSON layers under `public/data`:
roads, railways, waterways, waterbodies, and the derived flyover layer. OpenStreetMap data is © OpenStreetMap
contributors and is licensed under the Open Database License (ODbL).
The script also derives an OSM-based 3D flyover layer from bridge-tagged road
and railway ways, with inferred decks and piers for visualization.
