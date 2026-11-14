# Mandideep Web GIS

This is the main Mandideep map application. It is a standalone static site based on the Mohanpura Flood Observatory architecture:

- MapLibre map shell with ArcGIS Satellite as the default basemap.
- Local versioned GeoJSON assets; no Streamlit iframe and no Python runtime required to display the map.
- Terrain, 3D buildings, 3D tree canopies/trunks, AOI, buffer, OSM roads, railways, rivers/waterways, waterbodies, and an OSM-derived 3D flyover/pier layer as independently controlled layers. All project data layers are active by default. Tree point marks and tree area polygon are intentionally excluded. CAD, contours and feature labels are deferred for separate future layers.
- Environmental sunlight controls directional 3D shading, intensity, and azimuth for buildings, trees, terrain, and flyover decks/piers. MapLibre's bundled renderer provides surface/side shading rather than survey-grade cast-shadow simulation.
- Buildings use an off-white/peach palette with generated ground-shadow polygons; shadows respond to the sunlight azimuth and are visualization approximations, not photometric or engineering-grade shadow analysis.
- Building façades use a stable Coolors grey palette from `#f8f9fa` through `#212529`, assigned from each feature identifier so neighboring footprints remain distinct across reloads.
- The app building layer is a deduplicated merge of the current Overture/ML footprints and 3D-GloBFP India tile 1821, clipped to the updated AOI plus 100 m buffer.
- Optional fog and rain overlays are presentation effects for scene context; they are not meteorological observations or forecasts.
- Climate baseline: `tools/build_climate_exposure_proxy.py` creates a 100 m planning proxy from mapped building, road, tree-canopy, and water coverage. The result is `public/data/mandideep_climate_exposure_proxy_wgs84.geojson`; it is explicitly not a measured land-surface-temperature or air-temperature product. Satellite-derived LST/NDVI/NDBI and carbon modules remain the next evidence-based stage.
- Lazy loading keeps the 12 MB building layer out of the initial request path until it is enabled.
- Streamlit is retained only for analysis and data preparation, not for the main user-facing map.

Run locally from this directory:

```powershell
python -m http.server 8080
```

Then open `http://localhost:8080/`. A static server is required because browsers block `fetch()` from `file://` pages.

Do not double-click `index.html`; that produces the expected `Failed to fetch` message because GeoJSON is loaded with browser `fetch()` calls.

Data display CRS is WGS 84; source/analysis CRS is EPSG:32643 / UTM Zone 43N.

The approved AOI is sourced from `AOI Mandideep.kmz`, updated by
`tools/update_mandideep_aoi_from_kmz.py`, and has an area of approximately
17.963 km². Its 100 m buffer is regenerated from the approved boundary.

OSM layers are a bounded extract from the Overpass API. Source: OpenStreetMap
contributors, retrieved by `tools/fetch_osm.py`, licensed under the Open Database
License (ODbL). The extract is stored locally so the production map does not
depend on an Overpass request at runtime.

Roads are clipped by `tools/clip_osm_roads_to_aoi.py` in EPSG:32643 / UTM Zone
43N. The app uses `mandideep_osm_roads_buffer100m_wgs84.geojson` for context
around the AOI; `mandideep_osm_roads_aoi_wgs84.geojson` is also produced for
exact-AOI GIS use.

The flyover layer is a visualization approximation generated from OSM ways with
`bridge=*` tags. Deck widths, deck heights, and pier spacing are inferred for
display and must not be used as structural, clearance, or construction data.
