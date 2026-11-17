# NITA GeoAI Roads & Stormwater Geotagging

Mobile-first progressive web app for field inventory of roads, stormwater drainage, and their associated assets.

## Included

- Non-editable GPS capture with an in-form location map and accuracy circle
- High-accuracy multi-sample positioning that retains the best fix
- Road and stormwater asset catalogues
- Three individual photo slots: Photo 1 mandatory, Photos 2 and 3 optional
- Automatic on-device JPEG resizing and compression with size reporting
- Mobile-first field layout with large touch targets, compact maps, and a sticky save bar
- Read-only device date, time, ISO timestamp, and mobile timezone
- Mobile-safe Mandideep reference vectors from the 3D Scene: AOI, roads, waterways, waterbodies, railways, and flyovers
- Condition, dimensions, chainage, side, issue, and remarks
- Offline device storage and installable PWA shell
- Authenticated submission to the centralized NITA GeoAI Field Survey database
- Automatic retry of pending records when connectivity returns or the app becomes active
- Mobile-safe adaptive photo compression and explicit upload/storage failure messages
- Map/list review, editing, filtering, and deletion
- Leaflet basemap selection: satellite imagery, topographic, or OpenStreetMap
- GeoJSON, CSV, and full JSON survey-packet export
- Administrator dashboard for category, condition, spatial, GPS, photo-completeness, quality and register analysis

## Run locally

From the `Vastushilpi` folder (so the sibling Mandideep 3D Scene layers are available):

```powershell
python -m http.server 8080
```

Open `http://localhost:8080/roads_drainage_geotagging/` on a phone or computer for interface review. GPS and camera access require HTTPS in most hosted environments; `localhost` is accepted for development. Centralized submission requires the authenticated NITA GeoAI server endpoints and is not available from a standalone static server.

Open the administrator dashboard from **Export → Open administrator dashboard**, or visit `http://localhost:8080/roads_drainage_admin_dashboard/dist/`. Keep both apps on the same website origin so the dashboard can read the field records stored by the mobile app.

The dashboard is also packaged as one self-contained `dist/index.html` file for layout review when opened directly. Use the local server or the hosted NITA AI website for the complete Mandideep layers and shared browser storage.

## Production route

The managed form is published at:

`https://nitageoai.com/workspace/field-survey/roads-drainage/`

The production host supplies the protected session and record APIs. Never add server passwords, user passwords, session tokens, or database files to this repository.

## Data model

All coordinates are stored as longitude/latitude in WGS 84 (EPSG:4326). New records are queued safely on the device first and then synchronized to the authenticated NITA GeoAI database. Pending records retry automatically after temporary connectivity failures. Synchronized records retain lightweight metadata locally while photograph binaries remain protected on the server.

The interface follows the NITA AI & GEOANALYTICS AquaTwin brand palette and is ready to be packaged under the NITA AI website once its hosting target is selected.

## Verification

```powershell
python -m unittest discover -s tests -v
```

