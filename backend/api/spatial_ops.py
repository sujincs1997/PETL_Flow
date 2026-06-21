# Updated imports and corrected lambda functions
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .auth import get_current_user, RoleChecker
from ..database import get_db
import geopandas as gpd
import json
from shapely.geometry import shape

router = APIRouter(prefix="/spatial", tags=["spatial"])

# Only developers/admins can perform spatial ops that modify data
check_developer = RoleChecker(["Admin", "Developer"])

SUPPORTED_OPERATIONS = {
    "buffer": lambda gdf, params: gdf.buffer(params.get("distance", 10)),
    "simplify": lambda gdf, params: gdf.assign(geometry=gdf.geometry.apply(lambda geom: geom.simplify(params.get("tolerance", 0.5)))),
    "dissolve": lambda gdf, params: gdf.dissolve(),
    "intersect": lambda gdf, params: gdf.overlay(gpd.GeoDataFrame.from_features(params.get("features", [])), how="intersection"),
    "union": lambda gdf, params: gdf.unary_union,
    "clip": lambda gdf, params: gdf.clip(gpd.GeoDataFrame.from_features(params.get("clip_features", []))),
    "shortest_path": lambda gdf, params: gdf,  # placeholder for complex graph ops
    "nearest_feature": lambda gdf, params: gdf,  # placeholder
    "reproject": lambda gdf, params: gdf.to_crs(params.get("crs", "EPSG:4326")),
    "spatial_join": lambda gdf, params: gdf.sjoin(gpd.GeoDataFrame.from_features(params.get("join_features", [])), how=params.get("how", "inner")),
}

@router.post("/operate", status_code=status.HTTP_200_OK)
async def spatial_operate(
    payload: dict,
    db: Session = Depends(get_db),
    current_user = Depends(check_developer),
):
    """Perform a spatial operation on supplied GeoJSON.
    payload example:
    {
        "operation": "buffer",
        "geojson": { ... },
        "params": {"distance": 10}
    }
    """
    operation = payload.get("operation")
    if operation not in SUPPORTED_OPERATIONS:
        raise HTTPException(status_code=400, detail="Unsupported operation")
    geojson = payload.get("geojson")
    if not geojson:
        raise HTTPException(status_code=400, detail="Missing geojson")
    try:
        gdf = gpd.GeoDataFrame.from_features(geojson.get("features", []))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid GeoJSON: {e}")
    params = payload.get("params", {})
    try:
        result = SUPPORTED_OPERATIONS[operation](gdf, params)
        # Ensure result is GeoDataFrame
        if not isinstance(result, gpd.GeoDataFrame):
            # For unary_union returns GeometryCollection
            result = gpd.GeoDataFrame(geometry=[result])
        return {"geojson": json.loads(result.to_json())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

