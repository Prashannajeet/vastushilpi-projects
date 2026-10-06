VASTUSHILPI · SEPARATE SURVEY GIS MAPS

Open: double-click Start GIS Maps.command. Keep its Terminal window open.
The installed QGIS-LTR Python runtime runs the local DEM sampling service.
Maps:
  http://127.0.0.1:8765/grid
  http://127.0.0.1:8765/hiraundi
The service is local to this computer. Basemaps need internet. Leaflet and drawing libraries are stored locally.

Each map defaults to Esri satellite imagery. Switch to OpenTopoMap for topographic context.
Toggle the smooth DEM, smooth hillshade, 1 m contours and coverage outline; adjust DEM opacity.
Draw elevation profile: click successive route vertices; click the last vertex again to finish. Escape cancels.
Click any drawn line to obtain its profile. Hover over the chart to inspect distance/elevation and follow the route.
NoData stays blank: terrain is not invented across unsupported gaps.
Export CSV includes distance, elevation, native easting/northing, WGS84 longitude/latitude and EPSG code.
Use the right map toolbar to draw lines, polygons, rectangles or markers. Edit/Delete tools allow changes.
Drawings are stored separately per location in this browser. Export GeoJSON to retain them outside the browser.
Exports are also saved in Interactive_Maps/exports within this project, so browser download restrictions do not lose them.
Each export replaces the same location's previous export; rename an export if you want to retain multiple versions.
Print map uses an A3 landscape print style; enable background graphics in the browser print dialog.
For publication layouts, use the QGIS project layouts described below.

QGIS PROJECTS (outputs/GIS_Map_Package):
  grid_interactive_gis.qgz
  geolocation_interactive_gis.qgz
Satellite imagery is the default basemap; Topography is available in the Online basemaps group.
Layouts: original Terrain layout plus Satellite | Professional GIS layout and Topography | Professional GIS layout.
Original DEM is enabled as an elevation profile surface. In QGIS open the elevation profile panel, select
Original DEM | 0.5 m | elevation profile source, and draw a profile curve.
CAD layer groups and native projected coordinates are retained. Data paths are relative.

SMOOTH PRODUCTS (outputs):
  grid_dem_smooth_0p5m.tif, geolocation_dem_smooth_0p5m.tif
  grid_hillshade_smooth.tif, geolocation_hillshade_smooth.tif
Gaussian normalized convolution: sigma 1 m, 9 x 9 cells (radius 2 m), original NoData mask reinstated.
Hillshade: average of four light azimuths 225/270/315/360 degrees, altitude 45 degrees.
These are visualization derivatives, not a new validated interpolation method or EBK.
Profiles use the ORIGINAL 0.5 m TIN DEM with bilinear cell-centre sampling, not smoothed images.
Native projected distance is used. Samples normally every 0.5 m or finer, maximum 20,001 samples;
very long routes use a coarser interval, displayed in the profile panel. Maximum route length 100 km.
Web overlays are reduced display images warped to Web Mercator; native GeoTIFFs retain 0.5 m cells.

REFERENCE:
Grid EPSG:32643 (WGS84 / UTM43N), explicitly stated in source CAD.
Hiraundi EPSG:24379 (Kalianpur1975 / IndiaIIa), translated from CAD local grid using recorded GEODATA.
Kalianpur→WGS84 transformation stated accuracy 22 m: precise satellite alignment is unverified.
Vertical datum is unconfirmed for both. Coverage is an interpolation mask, not a legal boundary.
0.5 m cell size does not mean 0.5 m accuracy; source point spacing is 5 m / 10 m.

BASEMAP ATTRIBUTION / DOCUMENTATION:
https://support.esri.com/en-us/knowledge-base/what-is-the-correct-way-to-cite-an-arcgis-online-basema-000012040
https://opentopomap.org/about
https://www.openstreetmap.org/copyright
https://leafletjs.com/reference
https://leaflet.github.io/Leaflet.draw/docs/leaflet-draw-latest.html
Libraries: Leaflet1.9.4 (BSD2), Leaflet.draw1.0.4 (MIT), downloaded from unpkg npm distributions.
Basemaps fetched only as users view them; no bulk imagery copies are stored.

REBUILD:
From project root: Rscript Interactive_Maps/prepare_visuals.R
PROJ_LIB=/Applications/QGIS-LTR.app/Contents/Resources/proj /Applications/QGIS-LTR.app/Contents/MacOS/bin/python3 Interactive_Maps/build_assets.py
The QGIS update script additionally needs PYTHONPATH=/Applications/QGIS-LTR.app/Contents/Resources/python and QT_QPA_PLATFORM=offscreen.
Validation: Interactive_Maps/validation.json. Native DEM cell values, distance, coordinate roundtrip and smoothing coverage checked.
