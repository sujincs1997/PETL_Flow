import pandas as pd
import geopandas as gpd
from typing import Dict, Any
from .base import BaseNode, NodeParameter, PortMetadata
from .registry import register_node
import sqlalchemy as sa
import fiona

try:
    from geoalchemy2 import Geometry, WKTElement
    HAS_GEOALCHEMY = True
except ImportError:
    HAS_GEOALCHEMY = False

# Enable KML driver in Fiona
try:
    fiona.drvsupport.supported_drivers['KML'] = 'rw'
    fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
except Exception:
    pass


@register_node
class CSVWriter(BaseNode):
    type = "CSVWriter"
    name = "CSV Writer"
    category = "Writers"
    description = "Writes a DataFrame into a CSV file."
    
    parameters_schema = [
        NodeParameter(
            name="file_path",
            label="File Path",
            type="str",
            required=True,
            description="Absolute path to target file (e.g. C:/data/out.csv)"
        ),
        NodeParameter(
            name="delimiter",
            label="Delimiter",
            type="str",
            default=",",
            required=False
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="Input DataFrame", type="pandas")
    ]
    outputs_schema = [] # Sink node

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        df = input_data.get("input")
        if df is None:
            raise ValueError("Input data missing from 'input' port.")
        
        path = self.params["file_path"]
        delim = self.params["delimiter"]
        
        # If it's a GeoDataFrame, we convert geometry to WKT for normal CSV output
        if isinstance(df, gpd.GeoDataFrame):
            df_out = df.copy()
            if "geometry" in df_out.columns:
                df_out["geometry"] = df_out["geometry"].apply(lambda geom: geom.wkt if geom else None)
            df_out.to_csv(path, sep=delim, index=False)
        else:
            df.to_csv(path, sep=delim, index=False)
            
        return {}


@register_node
class GeoJSONWriter(BaseNode):
    type = "GeoJSONWriter"
    name = "GeoJSON Writer"
    category = "Writers"
    description = "Writes a GeoDataFrame into a GeoJSON file."
    
    parameters_schema = [
        NodeParameter(
            name="file_path",
            label="File Path",
            type="str",
            required=True,
            description="Target file name with .geojson extension"
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="GeoDataFrame", type="geopandas")
    ]
    outputs_schema = []

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        gdf = input_data.get("input")
        if gdf is None:
            raise ValueError("Input GeoDataFrame missing from 'input' port.")
        
        if not isinstance(gdf, gpd.GeoDataFrame):
            # Try to promote standard pandas to geopandas if geometry exists as WKT
            if "geometry" in gdf.columns:
                from shapely import wkt
                gdf["geometry"] = gdf["geometry"].apply(wkt.loads)
                gdf = gpd.GeoDataFrame(gdf, geometry="geometry")
            else:
                raise TypeError("Input must be a GeoDataFrame to write GeoJSON.")
                
        path = self.params["file_path"]
        gdf.to_file(path, driver="GeoJSON")
        return {}


if HAS_GEOALCHEMY:
    @register_node
    class PostGISWriter(BaseNode):
        type = "PostGISWriter"
        name = "PostGIS Writer"
        category = "Writers"
        description = "Saves spatial data (GeoDataFrame) into a PostGIS table."
        
        parameters_schema = [
            NodeParameter(
                name="connection_string",
                label="Database Connection URI",
                type="str",
                required=True,
                description="postgresql://user:pass@host:5432/db"
            ),
            NodeParameter(
                name="table_name",
                label="Table Name",
                type="str",
                required=True
            ),
            NodeParameter(
                name="if_exists",
                label="If Table Exists",
                type="select",
                default="replace",
                options=["fail", "replace", "append"],
                required=False
            ),
            NodeParameter(
                name="srid",
                label="SRID",
                type="int",
                default=4326,
                required=False
            )
        ]
        
        inputs_schema = [
            PortMetadata(name="input", label="GeoDataFrame", type="geopandas")
        ]
        outputs_schema = []

        def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            gdf = input_data.get("input")
            if gdf is None:
                raise ValueError("Input data missing from 'input' port.")
                
            if not isinstance(gdf, gpd.GeoDataFrame):
                raise TypeError("Input must be a GeoDataFrame for PostGIS writing.")
                
            connection = self.params["connection_string"]
            table = self.params["table_name"]
            mode = self.params["if_exists"]
            srid = self.params["srid"]
            
            engine = sa.create_engine(connection)
            
            # Write to PostGIS using geoalchemy2 types if available
            # GeoPandas has built-in to_postgis support
            gdf.to_postgis(
                name=table,
                con=engine,
                if_exists=mode,
                schema="public",
                index=False,
                dtype={"geometry": Geometry(geometry_type="GEOMETRY", srid=srid)}
            )
            return {}
else:
    class PostGISWriter(BaseNode):
        type = "PostGISWriter"
        name = "PostGIS Writer"
        category = "Writers"
        description = "Saves spatial data (GeoDataFrame) into a PostGIS table. (PostgreSQL driver missing)"
        
        parameters_schema = []
        inputs_schema = []
        outputs_schema = []
        
        def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            raise ImportError("PostgreSQL client libraries (psycopg2/geoalchemy2) are missing. Run via Docker or install pg_config.")



@register_node
class ShapefileWriter(BaseNode):
    type = "ShapefileWriter"
    name = "Shapefile Writer"
    category = "Writers"
    description = "Writes a GeoDataFrame into an ESRI Shapefile."
    
    parameters_schema = [
        NodeParameter(
            name="file_path",
            label="File Path (.shp)",
            type="str",
            required=True,
            description="Target file name with .shp extension"
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="GeoDataFrame", type="geopandas")
    ]
    outputs_schema = []

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        gdf = input_data.get("input")
        if gdf is None:
            raise ValueError("Input GeoDataFrame missing from 'input' port.")
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame to write Shapefiles.")
            
        path = self.params["file_path"]
        gdf.to_file(path, driver="ESRI Shapefile")
        return {}


@register_node
class MapInfoWriter(BaseNode):
    type = "MapInfoWriter"
    name = "MapInfo Writer"
    category = "Writers"
    description = "Writes a GeoDataFrame into MapInfo TAB vector format."
    
    parameters_schema = [
        NodeParameter(
            name="file_path",
            label="File Path (.tab)",
            type="str",
            required=True,
            description="Target file name with .tab extension"
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="GeoDataFrame", type="geopandas")
    ]
    outputs_schema = []

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        gdf = input_data.get("input")
        if gdf is None:
            raise ValueError("Input GeoDataFrame missing from 'input' port.")
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame to write MapInfo files.")
            
        path = self.params["file_path"]
        gdf.to_file(path, driver="MapInfo File")
        return {}


@register_node
class SpatiaLiteWriter(BaseNode):
    type = "SpatiaLiteWriter"
    name = "SpatiaLite Writer"
    category = "Writers"
    description = "Writes a GeoDataFrame to a SQLite/SpatiaLite database layer."
    
    parameters_schema = [
        NodeParameter(
            name="file_path",
            label="SQLite DB Path",
            type="str",
            required=True,
            description="Path to target .sqlite file"
        ),
        NodeParameter(
            name="layer_name",
            label="Layer Name (Table)",
            type="str",
            required=True,
            description="Table name to write geometry into"
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="GeoDataFrame", type="geopandas")
    ]
    outputs_schema = []

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        gdf = input_data.get("input")
        if gdf is None:
            raise ValueError("Input GeoDataFrame missing from 'input' port.")
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame.")
            
        path = self.params["file_path"]
        layer = self.params["layer_name"]
        gdf.to_file(path, driver="SQLite", spatialite=True, layer=layer)
        return {}


@register_node
class GDBWriter(BaseNode):
    type = "GDBWriter"
    name = "GDB Writer"
    category = "Writers"
    description = "Writes a GeoDataFrame layer into an ESRI File Geodatabase (.gdb folder)."
    
    parameters_schema = [
        NodeParameter(
            name="folder_path",
            label="GDB Folder Path",
            type="str",
            required=True,
            description="Path to target .gdb directory"
        ),
        NodeParameter(
            name="layer_name",
            label="Layer Name",
            type="str",
            required=True,
            description="Feature class layer name inside the GDB"
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="GeoDataFrame", type="geopandas")
    ]
    outputs_schema = []

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        gdf = input_data.get("input")
        if gdf is None:
            raise ValueError("Input GeoDataFrame missing from 'input' port.")
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame.")
            
        path = self.params["folder_path"]
        layer = self.params["layer_name"]
        gdf.to_file(path, driver="OpenFileGDB", layer=layer)
        return {}


@register_node
class KMLWriter(BaseNode):
    type = "KMLWriter"
    name = "KML Writer"
    category = "Writers"
    description = "Writes a GeoDataFrame into KML format."
    
    parameters_schema = [
        NodeParameter(
            name="file_path",
            label="KML File Path",
            type="str",
            required=True,
            description="Path to target .kml file"
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="GeoDataFrame", type="geopandas")
    ]
    outputs_schema = []

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        gdf = input_data.get("input")
        if gdf is None:
            raise ValueError("Input GeoDataFrame missing from 'input' port.")
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame to write KML.")
            
        path = self.params["file_path"]
        gdf.to_file(path, driver="KML")
        return {}

