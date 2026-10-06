"""Portable native-CRS DEM sampling for Vastushilpi Projects."""
from pathlib import Path
import math
import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer


def elevation_profile(path: Path, coordinates: list, interval=0.5) -> tuple[pd.DataFrame, dict]:
    if len(coordinates) < 2 or len(coordinates) > 1000:
        raise ValueError('Draw a line with 2–1,000 vertices.')
    coords = np.asarray(coordinates, dtype=float)
    if coords.ndim != 2 or coords.shape[1] != 2 or not np.isfinite(coords).all():
        raise ValueError('Profile coordinates must be longitude/latitude pairs.')
    if (np.abs(coords[:, 0]) > 180).any() or (np.abs(coords[:, 1]) > 90).any():
        raise ValueError('Invalid longitude/latitude.')
    with rasterio.open(path) as dem:
        if not dem.crs or not dem.crs.is_projected:
            raise ValueError('DEM must have a projected coordinate system in metres.')
        if abs(dem.crs.linear_units_factor[1] - 1) > 1e-6:
            raise ValueError('DEM horizontal units must be metres.')
        forward = Transformer.from_crs('EPSG:4326', dem.crs, always_xy=True)
        reverse = Transformer.from_crs(dem.crs, 'EPSG:4326', always_xy=True)
        x, y = forward.transform(coords[:, 0], coords[:, 1]); xy = np.column_stack([x, y])
        lengths = np.linalg.norm(np.diff(xy, axis=0), axis=1)
        cumulative = np.r_[0, np.cumsum(lengths)]; total = float(cumulative[-1])
        if total <= 0 or total > 100000:
            raise ValueError('Profile must be longer than zero and shorter than 100 km.')
        count = min(20001, max(2, math.ceil(total / interval) + 1))
        distances = np.linspace(0, total, count)
        indices = np.minimum(np.searchsorted(cumulative, distances, side='right') - 1, len(lengths) - 1)
        fractions = np.divide(distances - cumulative[indices], lengths[indices], out=np.zeros(count), where=lengths[indices] > 0)
        pts = xy[indices] + fractions[:, None] * (xy[indices + 1] - xy[indices])
        inv = ~dem.transform
        pixel = np.array([inv * tuple(p) for p in pts]) - 0.5
        c, r = pixel[:, 0], pixel[:, 1]
        inside = (c >= -.5) & (r >= -.5) & (c <= dem.width - .5) & (r <= dem.height - .5)
        z = np.full(count, np.nan)
        # Read the smallest bounding window; no global raster cache or shared file handles.
        if inside.any():
            cv = np.clip(c[inside], 0, dem.width - 1); rv = np.clip(r[inside], 0, dem.height - 1)
            i = cv.astype(int); j = rv.astype(int); i1 = np.minimum(i+1, dem.width-1); j1 = np.minimum(j+1, dem.height-1)
            x0, y0 = int(i.min()), int(j.min()); x1, y1 = int(i1.max()), int(j1.max())
            values = dem.read(1, window=rasterio.windows.Window(x0, y0, x1-x0+1, y1-y0+1), masked=True).astype(float).filled(np.nan)
            corners = np.column_stack([values[j-y0, i-x0], values[j-y0, i1-x0], values[j1-y0, i-x0], values[j1-y0, i1-x0]])
            dc, dr = cv-i, rv-j
            weights = np.column_stack([(1-dc)*(1-dr), dc*(1-dr), (1-dc)*dr, dc*dr])
            good = np.all(np.isfinite(corners) | (weights < 1e-10), axis=1)
            zz = np.sum(np.nan_to_num(corners)*weights, axis=1); zz[~good] = np.nan; z[inside] = zz
        lon, lat = reverse.transform(pts[:, 0], pts[:, 1])
        df = pd.DataFrame({'distance_m': distances, 'elevation_m': z, 'easting_m': pts[:, 0], 'northing_m': pts[:, 1], 'longitude': lon, 'latitude': lat, 'epsg': dem.crs.to_epsg()})
        stats = {'length_m': total, 'sample_interval_m': total/(count-1), 'supported_percent': float(np.isfinite(z).mean()*100), 'epsg': dem.crs.to_epsg()}
        return df, stats
