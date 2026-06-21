# -*- coding: utf-8 -*-
"""
End-to-end test: Read a CSV -> Write it to a new CSV
Uses the ETL Flow REST API on localhost:8000
"""
import requests
import time
import os
import sys

# Force UTF-8 output on Windows
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
print(f"  [OK] Logged in. Token: {TOKEN[:20]}...")

# 2. Verify nodes are registered
print("\nSTEP 2 - Checking registered nodes...")
nodes_res = requests.get(f"{BASE}/nodes", headers=HEADERS)
node_types = [n["type"] for n in nodes_res.json()]
print(f"  [OK] Found {len(node_types)} node types: {node_types[:8]}...")
assert "CSVReader" in node_types, "CSVReader not registered!"
assert "CSVWriter" in node_types, "CSVWriter not registered!"

# 3. Create workflow (CSVReader -> CSVWriter)
print("\nSTEP 3 - Creating workflow...")

INPUT_CSV = os.path.abspath("backend/data/stores.csv").replace("\\", "/")
OUTPUT_CSV = os.path.abspath("backend/data/stores_output.csv").replace("\\", "/")

# Remove old output if exists
if os.path.exists(OUTPUT_CSV):
    os.remove(OUTPUT_CSV)

workflow_payload = {
    "name": "Test CSV Copy Pipeline",
    "description": "Read stores.csv and write a copy to stores_output.csv",
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
            "node_key": "writer_1",
            "type": "CSVWriter",
            "config": {
                "file_path": OUTPUT_CSV,
                "delimiter": ","
            },
            "pos_x": 500,
            "pos_y": 200
        }
    ],
    "edges": [
        {
            "source_node": "reader_1",
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
wf_data = wf_res.json()
WF_ID = wf_data["id"]
print(f"  [OK] Workflow created: id={WF_ID}")

# 4. Execute workflow
print("\nSTEP 4 - Executing workflow...")
exec_res = requests.post(f"{BASE}/executions/run/{WF_ID}", headers=HEADERS)
if exec_res.status_code not in (200, 201):
    print(f"  [FAIL] Execution trigger failed ({exec_res.status_code}): {exec_res.text}")
    exit(1)
exec_data = exec_res.json()
EXEC_ID = exec_data["id"]
print(f"  [OK] Execution started: id={EXEC_ID}, status={exec_data['status']}")

# 5. Poll execution status
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
                print(f"    [{log.get('log_level', 'INFO')}] {log.get('message', '')}")
        break
    elif status_val == "FAILED":
        print("  [FAIL] Execution FAILED!")
        if "logs" in pdata and pdata["logs"]:
            print("\n  --- Execution Logs ---")
            for log in pdata["logs"]:
                print(f"    [{log.get('log_level', 'INFO')}] {log.get('message', '')}")
        exit(1)
else:
    print("  [FAIL] Timed out waiting for execution to complete.")
    exit(1)

# 6. Verify output
print(f"\nSTEP 6 - Verifying output file at: {OUTPUT_CSV}")
if os.path.exists(OUTPUT_CSV):
    with open(OUTPUT_CSV, "r") as f:
        content = f.read()
    lines = content.strip().split("\n")
    print(f"  [OK] Output file exists! {len(lines)} lines (including header)")
    print(f"  Header: {lines[0]}")
    for line in lines[1:]:
        print(f"    {line}")
    
    # Compare with input
    with open(INPUT_CSV, "r") as f:
        input_content = f.read()
    if input_content.strip() == content.strip():
        print("\n  [OK] OUTPUT MATCHES INPUT - Pipeline works correctly!")
    else:
        print("\n  [WARN] Output differs from input (check delimiters/encoding)")
        print(f"  Input length: {len(input_content)}, Output length: {len(content)}")
else:
    print(f"  [FAIL] Output file NOT found at {OUTPUT_CSV}")
    exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)
