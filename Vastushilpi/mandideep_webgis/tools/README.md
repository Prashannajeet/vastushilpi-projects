# Data preparation tools

Run from the `mandideep_webgis` directory:

```powershell
python tools/fetch_osm.py
```

The script queries OpenStreetMap's Overpass API for the project bounding box,
then writes four versioned WGS 84 GeoJSON layers under `public/data`:
roads, railways, waterways, and waterbodies. OpenStreetMap data is © OpenStreetMap
contributors and is licensed under the Open Database License (ODbL).
