"""Build a transparent 100 m urban heat-exposure planning proxy.

This is not satellite-derived land-surface temperature. It combines mapped
building, road, tree-canopy, and water coverage to identify likely heat
exposure and cooling opportunity zones until a validated thermal raster is
available.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import box


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "public" / "data"
AOI_PATH = DATA_DIR / "mandideep_aoi_wgs84.geojson"
BUILDINGS_PATH = DATA_DIR / "mandideep_buildings_merged_3d_wgs84.geojson"
TREES_PATH = DATA_DIR / "mandideep_tree_3d_wgs84.geojson"
ROADS_PATH = DATA_DIR / "mandideep_osm_roads_buffer100m_wgs84.geojson"
WATER_PATH = DATA_DIR / "mandideep_osm_waterbodies_wgs84.geojson"
OUTPUT_PATH = DATA_DIR / "mandideep_climate_exposure_proxy_wgs84.geojson"
ANALYSIS_CRS = "EPSG:32643"
GRID_SIZE_M = 100


def read_valid(path: Path) -> gpd.GeoDataFrame:
    """Read a vector layer, repair invalid geometry, and require a CRS."""
    frame = gpd.read_file(path)
    if frame.crs is None:
        raise ValueError(f"Missing CRS: {path}")
    frame = frame.loc[frame.geometry.notna() & ~frame.geometry.is_empty].copy()
    frame.geometry = frame.geometry.make_valid()
    return frame.to_crs(ANALYSIS_CRS)


def clipped_area(source: gpd.GeoDataFrame, grid: gpd.GeoDataFrame) -> np.ndarray:
    """Return intersected area per grid cell in square metres."""
    if source.empty:
        return np.zeros(len(grid), dtype=float)
    source = source[["geometry"]]
    overlay = gpd.overlay(grid[["cell_id", "geometry"]], source, how="intersection", keep_geom_type=False)
    if overlay.empty:
        return np.zeros(len(grid), dtype=float)
    values = overlay.geometry.area.groupby(overlay["cell_id"]).sum()
    return grid["cell_id"].map(values).fillna(0).to_numpy(dtype=float)


def clipped_length(source: gpd.GeoDataFrame, grid: gpd.GeoDataFrame) -> np.ndarray:
    """Return intersected line length per grid cell in metres."""
    if source.empty:
        return np.zeros(len(grid), dtype=float)
    overlay = gpd.overlay(grid[["cell_id", "geometry"]], source[["geometry"]], how="intersection", keep_geom_type=False)
    if overlay.empty:
        return np.zeros(len(grid), dtype=float)
    values = overlay.geometry.length.groupby(overlay["cell_id"]).sum()
    return grid["cell_id"].map(values).fillna(0).to_numpy(dtype=float)


def minmax(values: np.ndarray) -> np.ndarray:
    """Scale finite values to 0–1, returning zeros for a constant field."""
    lo, hi = float(np.nanmin(values)), float(np.nanmax(values))
    if hi <= lo:
        return np.zeros_like(values, dtype=float)
    return (values - lo) / (hi - lo)


def build_grid(aoi: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Create a 100 m fishnet clipped to the approved AOI."""
    min_x, min_y, max_x, max_y = aoi.total_bounds
    cells = []
    cell_id = 0
    for x in np.arange(min_x, max_x, GRID_SIZE_M):
        for y in np.arange(min_y, max_y, GRID_SIZE_M):
            cells.append({"cell_id": cell_id, "geometry": box(x, y, x + GRID_SIZE_M, y + GRID_SIZE_M)})
            cell_id += 1
    grid = gpd.GeoDataFrame(cells, crs=ANALYSIS_CRS)
    return gpd.overlay(grid, aoi[["geometry"]], how="intersection", keep_geom_type=True)


def main() -> None:
    aoi = read_valid(AOI_PATH)
    buildings = read_valid(BUILDINGS_PATH)
    trees = read_valid(TREES_PATH)
    roads = read_valid(ROADS_PATH)
    water = read_valid(WATER_PATH)

    canopy = trees.loc[trees["part"].eq("canopy")].copy() if "part" in trees else trees
    grid = build_grid(aoi)
    cell_area = grid.geometry.area.to_numpy(dtype=float)
    building_area = clipped_area(buildings, grid)
    canopy_area = clipped_area(canopy, grid)
    water_area = clipped_area(water, grid)
    road_length = clipped_length(roads, grid)

    building_density = np.clip(building_area / cell_area, 0, 1)
    canopy_density = np.clip(canopy_area / cell_area, 0, 1)
    water_density = np.clip(water_area / cell_area, 0, 1)
    road_density = np.clip(road_length / (GRID_SIZE_M * 4), 0, 1)
    heat_raw = 0.62 * building_density + 0.23 * road_density - 0.95 * canopy_density - 0.35 * water_density
    heat_score = np.round(100 * minmax(heat_raw), 1)
    cooling_score = np.round(100 * np.clip(0.75 * canopy_density + 0.25 * water_density, 0, 1), 1)

    grid["building_pct"] = np.round(building_density * 100, 2)
    grid["canopy_pct"] = np.round(canopy_density * 100, 2)
    grid["water_pct"] = np.round(water_density * 100, 2)
    grid["road_m"] = np.round(road_length, 1)
    grid["heat_proxy"] = heat_score
    grid["cooling_score"] = cooling_score
    grid["heat_class"] = np.select(
        [heat_score >= 66, heat_score >= 33], ["High exposure", "Moderate exposure"], default="Lower exposure"
    )
    grid["source_note"] = "Planning proxy: buildings + roads - tree canopy - water; not satellite LST"

    output = grid.to_crs("EPSG:4326")
    output.to_file(OUTPUT_PATH, driver="GeoJSON")
    summary = {
        "analysis_crs": ANALYSIS_CRS,
        "display_crs": "EPSG:4326",
        "grid_size_m": GRID_SIZE_M,
        "cells": len(output),
        "aoi_area_km2": round(float(aoi.to_crs(ANALYSIS_CRS).geometry.area.sum() / 1_000_000), 3),
        "heat_proxy_definition": "0.62 building density + 0.23 road density - 0.95 canopy density - 0.35 water density",
        "limitation": "Not a measured land-surface-temperature or air-temperature product.",
    }
    (DATA_DIR / "mandideep_climate_exposure_proxy_metadata.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
