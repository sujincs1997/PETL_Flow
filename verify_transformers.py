import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from backend.nodes.transformations import AttributeCreator
from backend.nodes.gis import SpatialRelator

def test_attribute_creator():
    print("--- Testing AttributeCreator ---")
    data = pd.DataFrame([
        {"first_name": "John", "last_name": "Doe", "age": 30},
        {"first_name": "Jane", "last_name": "Smith", "age": 25}
    ])
    
    # Configure AttributeCreator node
    config = {
        "attributes": '{"full_name": "first_name + \' \' + last_name", "category": "\'Adult\'", "next_year_age": "age + 1", "score": 99.5}'
    }
    node = AttributeCreator("node_1", config)
    res = node.execute({"input": data})
    output_df = res["output"]
    print("Input DataFrame:")
    print(data)
    print("Output DataFrame:")
    print(output_df)
    
    assert "full_name" in output_df.columns
    assert output_df.loc[0, "full_name"] == "John Doe"
    assert output_df.loc[1, "full_name"] == "Jane Smith"
    assert output_df.loc[0, "category"] == "Adult"
    assert output_df.loc[0, "next_year_age"] == 31
    assert output_df.loc[0, "score"] == 99.5
    print("AttributeCreator tests PASSED successfully!\n")

def test_spatial_relator():
    print("--- Testing SpatialRelator ---")
    # Base features (e.g. Regions/Polygons)
    poly1 = Polygon([(0,0), (2,0), (2,2), (0,2)]) # Box from 0 to 2
    poly2 = Polygon([(3,3), (5,3), (5,5), (3,5)]) # Box from 3 to 5
    base_gdf = gpd.GeoDataFrame(
        {"region_id": ["R1", "R2"]}, 
        geometry=[poly1, poly2], 
        crs="EPSG:4326"
    )
    
    # Candidate features (e.g. Points)
    pt1 = Point(1, 1)    # Inside R1
    pt2 = Point(0.5, 0.5) # Inside R1
    pt3 = Point(4, 4)    # Inside R2
    pt4 = Point(10, 10)  # Outside everything
    candidate_gdf = gpd.GeoDataFrame(
        {"point_id": ["P1", "P2", "P3", "P4"], "val": [10, 20, 30, 40]}, 
        geometry=[pt1, pt2, pt3, pt4], 
        crs="EPSG:4326"
    )
    
    # Configure SpatialRelator node
    # Relation: contains (base contains candidate)
    config = {
        "spatial_relation": "contains",
        "count_attribute": "_cnt",
        "matched_attribute": "_is_match",
        "candidate_attribute": "point_id",
        "candidate_attribute_agg": "list"
    }
    
    node = SpatialRelator("node_2", config)
    res = node.execute({"base": base_gdf, "candidate": candidate_gdf})
    output_gdf = res["output"]
    
    print("Base GeoDataFrame:")
    print(base_gdf)
    print("Candidate GeoDataFrame:")
    print(candidate_gdf)
    print("Output GeoDataFrame:")
    print(output_gdf)
    
    assert "_cnt" in output_gdf.columns
    assert "_is_match" in output_gdf.columns
    assert "_candidate_point_id" in output_gdf.columns
    
    assert output_gdf.loc[0, "_cnt"] == 2
    assert output_gdf.loc[0, "_is_match"] == True
    assert set(output_gdf.loc[0, "_candidate_point_id"]) == {"P1", "P2"}
    
    assert output_gdf.loc[1, "_cnt"] == 1
    assert output_gdf.loc[1, "_is_match"] == True
    assert output_gdf.loc[1, "_candidate_point_id"] == ["P3"]
    
    print("SpatialRelator tests PASSED successfully!\n")

if __name__ == "__main__":
    test_attribute_creator()
    test_spatial_relator()
