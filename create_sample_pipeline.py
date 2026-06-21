import uuid
from backend.database import engine
from backend.models.user import User
from backend.models.workflow import Workflow, Node, Edge
from sqlalchemy.orm import Session

def create_sample_pipeline():
    with Session(engine) as db:
        # Get the owner user 'testuser'
        user = db.query(User).filter(User.username == "testuser").first()
        if not user:
            print("Please run query_nodes.py first to create the testuser.")
            return
            
        # Check if this sample workflow already exists
        existing = db.query(Workflow).filter(Workflow.name == "Sample GIS Pipeline (Attribute Creator & Spatial Relator)").first()
        if existing:
            print("Sample workflow already exists in the database.")
            return

        workflow_id = uuid.uuid4()
        new_workflow = Workflow(
            id=workflow_id,
            name="Sample GIS Pipeline (Attribute Creator & Spatial Relator)",
            description="Loads CSV data, formats attributes with Attribute Creator, creates Point geometries, matches them against zones using Spatial Relator, and outputs to GeoJSON.",
            version=1,
            owner_id=user.id
        )
        db.add(new_workflow)

        # 1. Add CSVReader Node
        n1 = Node(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            node_key="csv_reader_1",
            type="CSVReader",
            config={
                "file_path": "backend/data/stores.csv",
                "delimiter": ",",
                "has_header": True
            },
            pos_x=100.0,
            pos_y=200.0
        )
        # 2. Add AttributeCreator Node
        n2 = Node(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            node_key="attr_creator_1",
            type="AttributeCreator",
            config={
                "attributes": '{"full_name": "first_name + \' \' + last_name", "category": "\'Retail Store\'", "score": 85.5}'
            },
            pos_x=350.0,
            pos_y=200.0
        )
        # 3. Add PointCreatorNode
        n3 = Node(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            node_key="point_creator_1",
            type="PointCreatorNode",
            config={
                "longitude_col": "longitude",
                "latitude_col": "latitude",
                "crs": "EPSG:4326"
            },
            pos_x=600.0,
            pos_y=200.0
        )
        # 4. Add GeoJSONReader Node (Candidate Layer)
        n4 = Node(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            node_key="geojson_reader_1",
            type="GeoJSONReader",
            config={
                "file_path": "backend/data/zones.geojson"
            },
            pos_x=600.0,
            pos_y=420.0
        )
        # 5. Add SpatialRelator Node
        n5 = Node(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            node_key="spatial_relator_1",
            type="SpatialRelator",
            config={
                "spatial_relation": "within",
                "count_attribute": "_related_count",
                "matched_attribute": "_matched",
                "candidate_attribute": "zone_name",
                "candidate_attribute_agg": "first"
            },
            pos_x=900.0,
            pos_y=300.0
        )
        # 6. Add GeoJSONWriter Node
        n6 = Node(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            node_key="geojson_writer_1",
            type="GeoJSONWriter",
            config={
                "file_path": "backend/data/output_stores_with_zones.geojson"
            },
            pos_x=1200.0,
            pos_y=300.0
        )

        db.add_all([n1, n2, n3, n4, n5, n6])

        # Add Edges
        e1 = Edge(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            source_node="csv_reader_1",
            target_node="attr_creator_1",
            source_handle="output",
            target_handle="input"
        )
        e2 = Edge(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            source_node="attr_creator_1",
            target_node="point_creator_1",
            source_handle="output",
            target_handle="input"
        )
        e3 = Edge(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            source_node="point_creator_1",
            target_node="spatial_relator_1",
            source_handle="output",
            target_handle="base"
        )
        e4 = Edge(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            source_node="geojson_reader_1",
            target_node="spatial_relator_1",
            source_handle="output",
            target_handle="candidate"
        )
        e5 = Edge(
            id=uuid.uuid4(),
            workflow_id=workflow_id,
            source_node="spatial_relator_1",
            target_node="geojson_writer_1",
            source_handle="output",
            target_handle="input"
        )

        db.add_all([e1, e2, e3, e4, e5])
        db.commit()
        print("Sample GIS pipeline successfully added to database under workflow ID:", workflow_id)

if __name__ == "__main__":
    create_sample_pipeline()
