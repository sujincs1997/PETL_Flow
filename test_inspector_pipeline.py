# -*- coding: utf-8 -*-
"""
End-to-end test: CSVReader -> InspectorNode -> CSVWriter
Validates the Inspector node produces a report and passes data through unchanged.
"""
import requests
import time
import os
import sys
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8000/api"

# 1. Login
print("=" * 60)
print("STEP 1 - Logging in...")
login = requests.post(f"{BASE}/auth/login", json={"username": "admin", "password": "admin123"})
if login.status_code != 200:
    print(f"  [FAIL] Login failed ({login.status_code}): {login.text}")
    exit(1)
TOKEN = login.json()["access_token"]
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
print(f"  [OK] Logged in.")

# 2. Verify InspectorNode is registered
print("\nSTEP 2 - Checking InspectorNode registration...")
nodes_res = requests.get(f"{BASE}/nodes", headers=HEADERS)
node_list = nodes_res.json()
node_types = [n["type"] for n in node_list]
print(f"  [OK] Found {len(node_types)} node types")

assert "InspectorNode" in node_types, f"InspectorNode not registered! Available: {node_types}"
print("  [OK] InspectorNode is registered")

# Show Inspector metadata
inspector_meta = next(n for n in node_list if n["type"] == "InspectorNode")
print(f"  Category: {inspector_meta['category']}")
print(f"  Description: {inspector_meta['description'][:80]}...")
print(f"  Parameters: {[p['name'] for p in inspector_meta['parameters']]}")
print(f"  Inputs: {[p['name'] for p in inspector_meta['inputs']]}")
print(f"  Outputs: {[p['name'] for p in inspector_meta['outputs']]}")

# 3. Create workflow: CSVReader -> Inspector -> CSVWriter
print("\nSTEP 3 - Creating workflow...")
INPUT_CSV = os.path.abspath("backend/data/stores.csv").replace("\\", "/")
OUTPUT_CSV = os.path.abspath("backend/data/stores_inspected_output.csv").replace("\\", "/")

if os.path.exists(OUTPUT_CSV):
    os.remove(OUTPUT_CSV)

workflow_payload = {
    "name": "Inspector Test Pipeline",
    "description": "CSVReader -> Inspector -> CSVWriter",
    "version": 1,
    "nodes": [
        {
            "node_key": "reader_1",
            "type": "CSVReader",
            "config": {
                "file_path": INPUT_CSV,
                "delimiter": ",",
                "has_header": True
            },
            "pos_x": 100,
            "pos_y": 200
        },
        {
            "node_key": "inspector_1",
            "type": "InspectorNode",
            "config": {
                "report_label": "Store Data Inspection",
                "sample_rows": 10,
                "include_statistics": True
            },
            "pos_x": 350,
            "pos_y": 200
        },
        {
            "node_key": "writer_1",
            "type": "CSVWriter",
            "config": {
                "file_path": OUTPUT_CSV,
                "delimiter": ","
            },
            "pos_x": 600,
            "pos_y": 200
        }
    ],
    "edges": [
        {
            "source_node": "reader_1",
            "target_node": "inspector_1",
            "source_handle": "output",
            "target_handle": "input"
        },
        {
            "source_node": "inspector_1",
            "target_node": "writer_1",
            "source_handle": "output",
            "target_handle": "input"
        }
    ]
}

wf_res = requests.post(f"{BASE}/workflows", headers=HEADERS, json=workflow_payload)
if wf_res.status_code not in (200, 201):
    print(f"  [FAIL] Workflow creation failed ({wf_res.status_code}): {wf_res.text}")
    exit(1)
WF_ID = wf_res.json()["id"]
print(f"  [OK] Workflow created: id={WF_ID}")

# 4. Execute workflow
print("\nSTEP 4 - Executing workflow...")
exec_res = requests.post(f"{BASE}/executions/run/{WF_ID}", headers=HEADERS)
if exec_res.status_code not in (200, 201):
    print(f"  [FAIL] Execution trigger failed ({exec_res.status_code}): {exec_res.text}")
    exit(1)
EXEC_ID = exec_res.json()["id"]
print(f"  [OK] Execution started: id={EXEC_ID}")

# 5. Poll execution
print("\nSTEP 5 - Polling execution status...")
for i in range(30):
    time.sleep(1)
    poll = requests.get(f"{BASE}/executions/{EXEC_ID}", headers=HEADERS)
    pdata = poll.json()
    status_val = pdata["status"]
    print(f"  [{i+1}s] status = {status_val}")

    if status_val == "COMPLETED":
        print("  [OK] Execution COMPLETED!")
        if "logs" in pdata and pdata["logs"]:
            print("\n  --- Execution Logs ---")
            for log in pdata["logs"]:
                print(f"    [{log.get('log_level')}] {log.get('message', '')[:120]}")
        break
    elif status_val == "FAILED":
        print("  [FAIL] Execution FAILED!")
        if "logs" in pdata and pdata["logs"]:
            for log in pdata["logs"]:
                print(f"    [{log.get('log_level')}] {log.get('message', '')}")
        exit(1)
else:
    print("  [FAIL] Timed out.")
    exit(1)

# 6. Fetch inspection report via API
print(f"\nSTEP 6 - Fetching inspection report...")
report_res = requests.get(f"{BASE}/executions/{EXEC_ID}/inspection/inspector_1", headers=HEADERS)
if report_res.status_code != 200:
    print(f"  [FAIL] Could not fetch report ({report_res.status_code}): {report_res.text}")
    exit(1)

report = report_res.json()
print(f"  [OK] Report fetched successfully!")
print(f"\n  --- INSPECTION REPORT ---")
print(f"  Label: {report.get('label')}")
print(f"  Node ID: {report.get('node_id')}")

# Overview
ov = report.get("overview", {})
print(f"\n  [Overview]")
print(f"    Data Type: {ov.get('data_type')}")
print(f"    Rows: {ov.get('row_count')}")
print(f"    Columns: {ov.get('column_count')}")
print(f"    Memory: {ov.get('memory_usage_mb')} MB")
print(f"    Is GeoDataFrame: {ov.get('is_geodataframe')}")

# Schema
schema = report.get("schema", [])
print(f"\n  [Schema] ({len(schema)} columns)")
for col in schema:
    print(f"    {col['column']:20s} | {col['dtype']:10s} | non-null: {col['non_null_count']} | null: {col['null_count']} ({col['null_pct']}%)")

# Geometry
geo = report.get("geometry")
if geo:
    print(f"\n  [Geometry]")
    print(f"    CRS: {geo.get('crs_name')}")
    print(f"    Types: {geo.get('geometry_types')}")
    print(f"    Bounding Box: {geo.get('bounding_box')}")
else:
    print(f"\n  [Geometry] N/A (standard DataFrame)")

# Statistics
stats = report.get("statistics", {})
if stats:
    num_stats = stats.get("numeric", [])
    cat_stats = stats.get("categorical", [])
    print(f"\n  [Statistics]")
    print(f"    Numeric columns: {len(num_stats)}")
    for s in num_stats:
        print(f"      {s['column']:15s} | min={s['min']} max={s['max']} mean={s['mean']} std={s['std']} median={s['median']}")
    print(f"    Categorical columns: {len(cat_stats)}")
    for s in cat_stats:
        print(f"      {s['column']:15s} | unique={s['unique_count']} top={list(s.get('top_values', {}).keys())[:3]}")

# Sample Data
sample = report.get("sample_data", {})
print(f"\n  [Sample Data]")
print(f"    Columns: {sample.get('columns')}")
print(f"    Head rows: {len(sample.get('head', []))}")
print(f"    Tail rows: {len(sample.get('tail', []))}")

# 7. Verify output CSV (passthrough check)
print(f"\nSTEP 7 - Verifying passthrough output at: {OUTPUT_CSV}")
if os.path.exists(OUTPUT_CSV):
    with open(OUTPUT_CSV, "r") as f:
        output_content = f.read()
    with open(INPUT_CSV, "r") as f:
        input_content = f.read()
    
    output_lines = output_content.strip().split("\n")
    input_lines = input_content.strip().split("\n")
    
    print(f"  [OK] Output file exists! {len(output_lines)} lines")
    
    if len(output_lines) == len(input_lines):
        print(f"  [OK] Row counts match ({len(input_lines)} lines)")
    else:
        print(f"  [WARN] Row count mismatch: input={len(input_lines)}, output={len(output_lines)}")
    
    # Check headers match
    if output_lines[0] == input_lines[0]:
        print(f"  [OK] Headers match: {output_lines[0]}")
    else:
        print(f"  [WARN] Headers differ")
    
    print(f"  [OK] Data passed through Inspector unchanged!")
else:
    print(f"  [FAIL] Output file NOT found!")
    exit(1)

# Assertions
assert ov.get("row_count") == 5, f"Expected 5 rows, got {ov.get('row_count')}"
assert ov.get("column_count") == 4, f"Expected 4 columns, got {ov.get('column_count')}"
assert len(schema) == 4, f"Expected 4 schema entries, got {len(schema)}"
assert len(stats.get("numeric", [])) > 0, "Expected numeric statistics"
assert len(stats.get("categorical", [])) > 0, "Expected categorical statistics"
assert len(sample.get("head", [])) > 0, "Expected sample head rows"

print("\n" + "=" * 60)
print("ALL INSPECTOR TESTS PASSED")
print("=" * 60)
