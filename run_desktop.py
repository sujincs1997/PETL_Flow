import os
import sys
import subprocess
import time
import webbrowser
import threading

def install_backend_deps():
    print(">>> Installing backend python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--only-binary", ":all:", "-r", "backend/requirements.txt"])
        print(">>> Backend dependencies installed successfully.")
    except Exception as e:
        print(f"Error installing backend dependencies: {e}")
        sys.exit(1)

def install_frontend_deps():
    print(">>> Installing frontend npm dependencies...")
    # Ensure Node.js is in PATH (common install location)
    node_path = r"C:\Program Files\nodejs"
    if node_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{os.environ.get('PATH', '')};{node_path}"
    try:
        # Check if node is installed
        subprocess.check_output(["node", "--version"], shell=True)
    except Exception:
        print("Error: Node.js (npm) is not installed or not in your PATH.")
        print("Please install Node.js from https://nodejs.org/ before running.")
        sys.exit(1)

    try:
        # Run npm install inside frontend folder
        subprocess.check_call("npm install", shell=True, cwd="frontend")
        print(">>> Frontend dependencies installed successfully.")
    except Exception as e:
        print(f"Error installing frontend dependencies: {e}")
        sys.exit(1)

def start_backend():
    print(">>> Starting FastAPI backend server on http://localhost:8000...")
    # Change working directory to backend
    env = os.environ.copy()
    # Force SQLite for desktop runs
    env["DATABASE_URL"] = "sqlite:///./etl_flow.db"
    
    cwd = os.path.join(os.getcwd(), "backend")
    subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"], cwd=cwd, env=env)

def start_frontend():
    print(">>> Starting Vite React frontend server on http://localhost:3000...")
    cwd = os.path.join(os.getcwd(), "frontend")
    # run npm run dev
    subprocess.Popen("npm run dev", shell=True, cwd=cwd)

def main():
    print("==================================================")
    print("      Visual GIS ETL Studio Desktop Launch        ")
    print("==================================================")
    
    # 1. Install dependencies
    install_backend_deps()
    install_frontend_deps()
    
    # 2. Boot up servers
    start_backend()
    time.sleep(2)  # Give uvicorn a second to bind
    
    start_frontend()
    time.sleep(3)  # Give Vite a second to start
    
    # 3. Open user browser
    url = "http://localhost:3000"
    print(f"\n>>> Opening visual editor in your browser: {url}")
    webbrowser.open(url)
    
    print("\n>>> System running. Press Ctrl+C in this terminal to shut down.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n>>> Shutting down processes. Goodbye!")

if __name__ == "__main__":
    main()
