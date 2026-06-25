<<<<<<< HEAD
# ETL Flow: Geospatial Data Pipeline Engine

![ETL Flow](https://img.shields.io/badge/Status-Active-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-18.x-61dafb.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

**ETL Flow** is a powerful, visual, and highly customizable Extract-Transform-Load (ETL) pipeline builder specifically tailored for Data Engineering and Geospatial Information Systems (GIS). It allows users to drag-and-drop functional processing nodes onto a canvas, wire them together, and execute complex data transformations dynamically.

Designed with inspiration from FME (Feature Manipulation Engine), ETL Flow bridges the gap between tabular datasets and spatial geometries.

---

## ✨ Key Features

### 🗺️ Visual Node-Based Editor
Model your data flows using a beautiful drag-and-drop canvas powered by `React Flow`. Connect Inputs, Transformers, and Outputs effortlessly.

### 🐍 Dynamic Python Scripting
Execute raw Python scripts directly inside the pipeline. The **Python Script Node** allows you to configure dynamic input and output ports straight from the UI. Route datasets dynamically using powerful dictionary mappings (`inputs_dict` and `outputs_dict`).

### 🧱 Custom Node Builder
No need to write backend boilerplate! Use the built-in **Custom Node Builder** in the sidebar to define custom Python classes directly from the browser. Specify custom input/output ports, parameters, and executable logic. The backend API compiles the code, saves it, and hot-registers the node into the system instantly.

### 🌍 Geographic Data Inspector
Analyze your data visually! Attach an **Inspector Node** to any part of your pipeline to inspect the flow state:
- **Sample Data**: View raw tabular data in an interactive table.
- **Statistics**: View column metadata, types, and counts.
- **Map View**: Automatically parses `geometry` columns (Well-Known Text) into GeoJSON, bounding the viewport to the shapes, and paints them interactively on a Leaflet map. Click any spatial feature to view its full tabular attributes!

### 🚀 High-Performance Backend
Powered by **FastAPI**, **Pandas**, and **GeoPandas**. The asynchronous execution engine runs tasks seamlessly, caching intermediate states locally so you can resume, debug, and inspect specific nodes without re-running the entire pipeline.

---

## 🏗️ Architecture

ETL Flow operates on a decoupled Client-Server architecture:
1. **Frontend (React + Vite + Zustand)**: A highly interactive canvas that maintains graph state and communicates pipeline definitions to the backend via REST API.
2. **Backend (FastAPI + SQLite)**: A robust python engine that serializes the visual graph, resolves dependencies (Topological Sort), and executes Python classes.

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.9+)
- npm or yarn

### 1. Backend Setup
Navigate to the `backend` directory and set up your Python environment:
```bash
=======
ETL Flow: Geospatial Data Pipeline Engine
ETL FlowPythonReactFastAPILicense

ETL Flow is a powerful, visual, and highly customizable Extract-Transform-Load (ETL) pipeline builder specifically tailored for Data Engineering and Geospatial Information Systems (GIS). It allows users to drag-and-drop functional processing nodes onto a canvas, wire them together, and execute complex data transformations dynamically.

Designed with inspiration from FME (Feature Manipulation Engine), ETL Flow bridges the gap between tabular datasets and spatial geometries.

✨ Key Features
🗺️ Visual Node-Based Editor
Model your data flows using a beautiful drag-and-drop canvas powered by React Flow. Connect Inputs, Transformers, and Outputs effortlessly.

🐍 Dynamic Python Scripting
Execute raw Python scripts directly inside the pipeline. The Python Script Node allows you to configure dynamic input and output ports straight from the UI. Route datasets dynamically using powerful dictionary mappings (inputs_dict and outputs_dict).

🧱 Custom Node Builder
No need to write backend boilerplate! Use the built-in Custom Node Builder in the sidebar to define custom Python classes directly from the browser. Specify custom input/output ports, parameters, and executable logic. The backend API compiles the code, saves it, and hot-registers the node into the system instantly.

🌍 Geographic Data Inspector
Analyze your data visually! Attach an Inspector Node to any part of your pipeline to inspect the flow state:

Sample Data: View raw tabular data in an interactive table.
Statistics: View column metadata, types, and counts.
Map View: Automatically parses geometry columns (Well-Known Text) into GeoJSON, bounding the viewport to the shapes, and paints them interactively on a Leaflet map. Click any spatial feature to view its full tabular attributes!
🚀 High-Performance Backend
Powered by FastAPI, Pandas, and GeoPandas. The asynchronous execution engine runs tasks seamlessly, caching intermediate states locally so you can resume, debug, and inspect specific nodes without re-running the entire pipeline.

🏗️ Architecture
ETL Flow operates on a decoupled Client-Server architecture:

Frontend (React + Vite + Zustand): A highly interactive canvas that maintains graph state and communicates pipeline definitions to the backend via REST API.
Backend (FastAPI + SQLite): A robust python engine that serializes the visual graph, resolves dependencies (Topological Sort), and executes Python classes.
🚀 Getting Started
Prerequisites
Node.js (v18+)
Python (v3.9+)
npm or yarn
1. Backend Setup
Navigate to the backend directory and set up your Python environment:

bash

>>>>>>> 863d79aac0f3df37c9c6b2350c080a20e9ecf54b
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
<<<<<<< HEAD
```
Start the FastAPI server:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The API and execution engine will now be available at `http://localhost:8000`.

### 2. Frontend Setup
Navigate to the `frontend` directory:
```bash
cd frontend
npm install
```
Start the Vite development server:
```bash
npm run dev
```
Open your browser and navigate to `http://localhost:3000`.

---

## 📖 How It Works (Usage)

1. **Drag Nodes**: Open the left sidebar and drag a node (e.g. `CSV Reader`) onto the canvas.
2. **Configure**: Click the node to open the Configuration Panel on the right. Point it to a valid file path or specify required parameters.
3. **Transform**: Drag a transformer node (e.g. `Python Script Node`) onto the canvas.
4. **Wire**: Drag a connection from the output port of the Reader to the input port of the Transformer.
5. **Inspect**: Attach an `Inspector Node` to the output of your transformer to view the results.
6. **Execute**: Click the **Run Workflow** button at the top right of the canvas. The engine will execute the pipeline and you can click the `View Inspection Report` button to view your geographic shapes on the map!

---

## 🛠️ Creating Custom Nodes

You can expand the capabilities of ETL Flow without touching the source code:
1. Click **Create Custom Node** in the left sidebar.
2. Define the node's Type ID, Display Name, and Category.
3. Use the **Port Management** UI to dynamically define how many Input and Output ports the node should have.
4. Add custom parameters (strings, ints, booleans).
5. Write your execution code natively in Python, reading from `inputs_dict` and writing to `outputs_dict`.
6. Click **Compile & Register**. The node is now permanently added to your toolkit!

---

## 📜 License
This project is licensed under the MIT License.
=======
Start the FastAPI server:

bash

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
The API and execution engine will now be available at http://localhost:8000.

2. Frontend Setup
Navigate to the frontend directory:

bash

cd frontend
npm install
Start the Vite development server:

bash

npm run dev
Open your browser and navigate to http://localhost:3000.

📖 How It Works (Usage)
Drag Nodes: Open the left sidebar and drag a node (e.g. CSV Reader) onto the canvas.
Configure: Click the node to open the Configuration Panel on the right. Point it to a valid file path or specify required parameters.
Transform: Drag a transformer node (e.g. Python Script Node) onto the canvas.
Wire: Drag a connection from the output port of the Reader to the input port of the Transformer.
Inspect: Attach an Inspector Node to the output of your transformer to view the results.
Execute: Click the Run Workflow button at the top right of the canvas. The engine will execute the pipeline and you can click the View Inspection Report button to view your geographic shapes on the map!
🛠️ Creating Custom Nodes
You can expand the capabilities of ETL Flow without touching the source code:

Click Create Custom Node in the left sidebar.
Define the node's Type ID, Display Name, and Category.
Use the Port Management UI to dynamically define how many Input and Output ports the node should have.
Add custom parameters (strings, ints, booleans).
Write your execution code natively in Python, reading from inputs_dict and writing to outputs_dict.
Click Compile & Register. The node is now permanently added to your toolkit!
📜 License
This project is licensed under the MIT License.



<img width="1907" height="950" alt="image" src="https://github.com/user-attachments/assets/505d8d4e-7528-4bd1-9e55-16cc84cb46e8" />

>>>>>>> 863d79aac0f3df37c9c6b2350c080a20e9ecf54b
