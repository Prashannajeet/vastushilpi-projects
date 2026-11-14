"""Create a smooth display raster from the 100 m climate planning proxy.

The source remains the reproducible 100 m analytical grid. This script only
creates a smoother cartographic display using cubic interpolation; it does
not turn the proxy into measured land-surface or air temperature.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
from PIL import Image
from pyproj import Transformer
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from scipy.interpolate import griddata
from shapely.geometry import shape


LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "public" / "data"
WIDTH = 1000
HEIGHT = 800
DISPLAY_BOUNDS = (77.5030283, 23.0624953, 77.5799250, 23.1164963)
COLORMAP = (
    (0.0, (103, 169, 207)),
    (25.0, (171, 217, 233)),
    (50.0, (254, 224, 139)),
    (75.0, (253, 174, 97)),
    (100.0, (215, 48, 39)),
)


def read_json(path: Path) -> dict:
    """Read a UTF-8 JSON document."""
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def interpolate_color(value: np.ndarray) -> np.ndarray:
    """Map values in the 0–100 proxy range to an RGB raster."""
    clipped = np.clip(value, 0.0, 100.0)
    result = np.zeros((*clipped.shape, 3), dtype=np.float32)
    for (lower_value, lower_color), (upper_value, upper_color) in zip(COLORMAP[:-1], COLORMAP[1:]):
        mask = (clipped >= lower_value) & (clipped <= upper_value)
        fraction = np.divide(
            clipped - lower_value,
            upper_value - lower_value,
            out=np.zeros_like(clipped),
            where=upper_value != lower_value,
        )
        for band in range(3):
            result[..., band] = np.where(
                mask,
                lower_color[band] + fraction * (upper_color[band] - lower_color[band]),
                result[..., band],
            )
    result[clipped >= COLORMAP[-1][0]] = COLORMAP[-1][1]
    return result.astype(np.uint8)


def build_raster() -> None:
    """Interpolate the planning proxy and write a transparent PNG overlay."""
    proxy = read_json(DATA_DIR / "mandideep_climate_exposure_proxy_wgs84.geojson")
    aoi = read_json(DATA_DIR / "mandideep_aoi_wgs84.geojson")
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True)

    centers: list[tuple[float, float]] = []
    values: list[float] = []
    for feature in proxy["features"]:
        geometry = shape(feature["geometry"])
        centroid = geometry.centroid
        centers.append(transformer.transform(centroid.x, centroid.y))
        values.append(float(feature["properties"].get("heat_proxy", 0.0)))

    west, south, east, north = DISPLAY_BOUNDS
    min_x, min_y = transformer.transform(west, south)
    max_x, max_y = transformer.transform(east, north)
    grid_x_values = np.linspace(min_x, max_x, WIDTH)
    grid_y_values = np.linspace(max_y, min_y, HEIGHT)
    grid_x, grid_y = np.meshgrid(grid_x_values, grid_y_values)
    cubic = griddata((np.array(centers)[:, 0], np.array(centers)[:, 1]), values, (grid_x, grid_y), method="cubic")
    nearest = griddata((np.array(centers)[:, 0], np.array(centers)[:, 1]), values, (grid_x, grid_y), method="nearest")
    smooth = np.nan_to_num(cubic, nan=nearest).clip(0.0, 100.0)

    aoi_shapes = [feature["geometry"] for feature in aoi["features"]]
    mask = rasterize(
        [(geometry, 1) for geometry in aoi_shapes],
        out_shape=(HEIGHT, WIDTH),
        transform=from_bounds(west, south, east, north, WIDTH, HEIGHT),
        fill=0,
        dtype="uint8",
    ).astype(bool)
    rgb = interpolate_color(smooth)
    alpha = np.where(mask, 165, 0).astype(np.uint8)
    rgba = np.dstack((rgb, alpha))
    output = DATA_DIR / "mandideep_climate_exposure_proxy_cubic.png"
    Image.fromarray(rgba, mode="RGBA").save(output, optimize=True)

    metadata = {
        "source": "mandideep_climate_exposure_proxy_wgs84.geojson",
        "method": "Cubic interpolation for cartographic display, nearest-neighbor fill outside cubic convex hull",
        "analysis_crs": "EPSG:32643",
        "display_crs": "EPSG:4326",
        "bounds": list(DISPLAY_BOUNDS),
        "width": WIDTH,
        "height": HEIGHT,
        "limitation": "Smooth planning proxy only; not measured land-surface temperature or air temperature.",
    }
    with (DATA_DIR / "mandideep_climate_exposure_proxy_cubic_metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
    LOGGER.info("Wrote %s (%sx%s) from %s cells", output, WIDTH, HEIGHT, len(values))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    build_raster()
