VASTUSHILPI - CONSOLIDATED CAD / GIS PROJECT

Project root: /Users/prashannajeet/Documents/Programming Learn/Vastushilpi

Source_CAD/                  Original source DWGs (moved, not duplicated)
outputs/                     Current GIS data, spatial references, reports, scripts
outputs/GIS_Map_Package/      QGIS projects, editable A3 layouts, PDF/PNG maps
outputs/Shapefiles/           Individual layers for both survey locations
outputs/Spatial_Reference/   CRS definitions, placement evidence, verification
 audit_logs/                 Processing and quality-assurance logs

Open either QGIS project:
outputs/GIS_Map_Package/grid_terrain.qgz
outputs/GIS_Map_Package/geolocation_terrain.qgz

Grid: EPSG:32643 (WGS 84 / UTM zone 43N).
Hiraundi: EPSG:24379 (Kalianpur 1975 / India zone IIa), placed from CAD GEODATA.
DEMs retain 0.5 m cells; a separate existing 0.1 m DEM has not been supplied.

Duplicate working outputs were replaced with relative symbolic links. The
canonical rasters, survey GeoPackages and XYZ CSVs are in outputs/. QGIS's data/
folder follows links to those canonical files. Keep this complete project folder
together when moving it. Identical report/script copies also use relative links.

Duplicate ZIP bundles and generated conversion/installation caches were removed.
Rebuildable intermediates can be recreated in work/ when needed. Audit logs and
the original raw-CAD interpolation recipe were preserved. Do not run the CRS
translation again on data already placed in EPSG:24379.

Run commands from this project root. For example, the existing R validation and
map-generation recipes use outputs/ and expect generated intermediates in work/.
R packages and GDAL/QGIS installed on this Mac were not removed. CAD conversion
requires LibreDWG; extraction additionally needs Python ezdxf (reinstall in a
project environment if needed). The deleted Python dependency cache is not source.

To recreate shareable ZIP bundles when needed:
python3 outputs/package_updated_gis.py

MIGRATION_REPORT.json records verification, removed duplicate archives, relative
aliases and disk space recovered. The previous Codex workspace contains only a
small PROJECT_MOVED.txt pointer.

INTERACTIVE GIS MAPS (6 October 2026)
Interactive_Maps/Start GIS Maps.command launches separate Grid and Hiraundi maps.
Satellite default, topography option, smooth DEM/hillshade, contours, editable drawing tools and original-DEM elevation profiles.
Interactive_Maps/README.txt provides instructions, limitations and rebuild steps.
New native QGIS projects: outputs/GIS_Map_Package/grid_interactive_gis.qgz and geolocation_interactive_gis.qgz.
Smooth native 0.5 m GeoTIFF products in outputs/ have .prj/.tfw sidecars.
