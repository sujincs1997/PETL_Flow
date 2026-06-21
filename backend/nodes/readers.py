import pandas as pd
import geopandas as gpd
from typing import Dict, Any, List
from .base import BaseNode, NodeParameter, PortMetadata
from .registry import register_node
import sqlalchemy as sa
import fiona

# Enable KML driver in Fiona
try:
    fiona.drvsupport.supported_drivers['KML'] = 'rw'
    fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
except Exception:
    pass

@register_node
class CSVReader(BaseNode):
    type = "CSVReader"
    name = "CSV Reader"
    category = "Readers"
    description = "Reads data from a CSV file into a Pandas DataFrame."
    
    parameters_schema = [
        NodeParameter(
            name="file_path",
            label="File Path or URL",
            type="str",
            required=True,
            description="Absolute path to local file, or HTTP/S3 URL"
        ),
        NodeParameter(
            name="delimiter",
            label="Delimiter",
            type="str",
            default=",",
            required=False
        ),
        NodeParameter(
            name="has_header",
            label="First Row as Header",
            type="bool",
            default=True,
            required=False
        )
    ]
    
    inputs_schema = [] # Source node
    outputs_schema = [
        PortMetadata(name="output", label="Output DataFrame", type="pandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        path = self.params["file_path"].replace('"', '').replace("'", '').strip()
        delim = self.params["delimiter"]
        header = 0 if self.params["has_header"] else None
        
        df = pd.read_csv(path, sep=delim, header=header)
        return {"output": df}


@register_node
class GeoJSONReader(BaseNode):
    type = "GeoJSONReader"
    name = "GeoJSON Reader"
    category = "Readers"
    description = "Reads geospatial features from a GeoJSON file or URL into a GeoDataFrame."
    
    parameters_schema = [
        NodeParameter(
            name="file_path",
            label="File Path or URL",
            type="str",
            required=True,
            description="Absolute path to a .geojson file or URL"
        )
    ]
    
    inputs_schema = []
    outputs_schema = [
        PortMetadata(name="output", label="GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        path = self.params["file_path"].replace('"', '').replace("'", '').strip()
        gdf = gpd.read_file(path)
        return {"output": gdf}


@register_node
class PostGISReader(BaseNode):
    type = "PostGISReader"
    name = "PostGIS Reader"
    category = "Readers"
    description = "Reads spatial data from a PostgreSQL database using PostGIS geometry features."
    
    parameters_schema = [
        NodeParameter(
            name="connection_string",
            label="Database Connection URI",
            type="str",
            required=True,
            description="postgresql://user:pass@host:5432/db"
        ),
        NodeParameter(
            name="query",
            label="SQL Query",
            type="sql",
            required=True,
            description="SELECT id, geom, attribute FROM my_table"
        ),
        NodeParameter(
            name="geom_col",
            label="Geometry Column Name",
            type="str",
            default="geom",
            required=True
        )
    ]
    
    inputs_schema = []
    outputs_schema = [
        PortMetadata(name="output", label="GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        uri = self.params["connection_string"]
        sql_query = self.params["query"]
        geom_col = self.params["geom_col"]
        
        engine = sa.create_engine(uri)
        gdf = gpd.read_postgis(sql_query, con=engine, geom_col=geom_col)
        return {"output": gdf}


@register_node
class ShapefileReader(BaseNode):
    type = "ShapefileReader"
    name = "Shapefile Reader"
    category = "Readers"
    description = "Reads geospatial features from an ESRI Shapefile."
    
    parameters_schema = [
        NodeParameter(
            name="folder_path",
            label="Shapefile Path",
            type="str",
            required=True,
            description="Absolute path to the .shp file"
        )
    ]
    
    inputs_schema = []
    outputs_schema = [
        PortMetadata(name="output", label="GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        path = self.params["folder_path"].replace('"', '').replace("'", '').strip()
        gdf = gpd.read_file(path)
        return {"output": gdf}


@register_node
class MapInfoReader(BaseNode):
    type = "MapInfoReader"
    name = "MapInfo Reader"
    category = "Readers"
    description = "Reads MapInfo vector datasets (TAB or MIF/MID format)."
    
    parameters_schema = [
        NodeParameter(
            name="file_path",
            label="File Path",
            type="str",
            required=True,
            description="Path to local MapInfo .tab or .mif file"
        )
    ]
    
    inputs_schema = []
    outputs_schema = [
        PortMetadata(name="output", label="GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        path = self.params["file_path"].replace('"', '').replace("'", '').strip()
        # GeoPandas read_file wraps fiona which automatically recognizes TAB/MIF drivers
        gdf = gpd.read_file(path)
        return {"output": gdf}


@register_node
class SpatiaLiteReader(BaseNode):
    type = "SpatiaLiteReader"
    name = "SpatiaLite Reader"
    category = "Readers"
    description = "Reads a geometry layer from a SpatiaLite/SQLite database file."
    
    parameters_schema = [
        NodeParameter(
            name="file_path",
            label="SQLite DB Path",
            type="str",
            required=True,
            description="Path to local .sqlite or .db file"
        ),
        NodeParameter(
            name="layer_name",
            label="Layer Name (Table)",
            type="str",
            required=True,
            description="Table name holding geometry"
        )
    ]
    
    inputs_schema = []
    outputs_schema = [
        PortMetadata(name="output", label="GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        path = self.params["file_path"].replace('"', '').replace("'", '').strip()
        layer = self.params["layer_name"]
        gdf = gpd.read_file(path, layer=layer)
        return {"output": gdf}


@register_node
class GDBReader(BaseNode):
    type = "GDBReader"
    name = "GDB Reader"
    category = "Readers"
    description = "Reads spatial layers from an ESRI File Geodatabase (.gdb folder)."
    
    parameters_schema = [
        NodeParameter(
            name="folder_path",
            label="GDB Folder Path",
            type="str",
            required=True,
            description="Path to the .gdb directory"
        ),
        NodeParameter(
            name="layer_name",
            label="Layer Name",
            type="str",
            required=True,
            description="Specific feature class layer inside the Geodatabase"
        )
    ]
    
    inputs_schema = []
    outputs_schema = [
        PortMetadata(name="output", label="GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        path = self.params["folder_path"].replace('"', '').replace("'", '').strip()
        layer = self.params["layer_name"]
        gdf = gpd.read_file(path, layer=layer)
        return {"output": gdf}


@register_node
class KMLReader(BaseNode):
    type = "KMLReader"
    name = "KML Reader"
    category = "Readers"
    description = "Reads geospatial features from a KML file."
    
    parameters_schema = [
        NodeParameter(
            name="file_path",
            label="KML File Path",
            type="str",
            required=True,
            description="Path to local KML file"
        )
    ]
    
    inputs_schema = []
    outputs_schema = [
        PortMetadata(name="output", label="GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Strip any literal quotes if the user pasted them in the UI
        path = self.params["file_path"].replace('"', '').replace("'", '').strip()
        
        # Fiona/GDAL is sensitive to Windows backslashes in paths
        path_safe = path.replace("\\", "/")
        
        try:
            # Try geopandas read_file first without driver explicitly, which sometimes works
            # if fiona/geopandas versions match up
            gdf = gpd.read_file(path_safe, driver="KML")
        except AttributeError:
            # Fallback for geopandas bug with fiona 1.9+ where fiona.path is missing
            import fiona
            from shapely.geometry import shape
            fiona.drvsupport.supported_drivers['KML'] = 'rw'
            fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
            with fiona.open(path_safe, 'r', driver='KML') as c:
                records = list(c)
                crs = c.crs
            geoms = [shape(rec['geometry']) if rec.get('geometry') else None for rec in records]
            props = [rec.get('properties', {}) for rec in records]
            gdf = gpd.GeoDataFrame(props, geometry=geoms, crs=crs)
            
        return {"output": gdf}

