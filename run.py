import subprocess
import sys
import os
import time

def start_backend():
    print("Starting backend server...")
    backend_process = subprocess.Popen([
        sys.executable, "backend/app.py"
    ], cwd=os.getcwd())
    return backend_process

def start_frontend():
    print("Starting frontend...")
    time.sleep(2)
    frontend_process = subprocess.Popen([
        "streamlit", "run", "frontend/app.py"
    ], cwd=os.getcwd())
    return frontend_process

if __name__ == "__main__":
    print("Starting Email Productivity Agent...")
    
    backend_process = start_backend()
    frontend_process = start_frontend()
    
    try:
        print("Application started successfully!")
        print("Backend: http://localhost:5000")
        print("Frontend: http://localhost:8501")
        print("\nPress Ctrl+C to stop the application")
        
        backend_process.wait()
        frontend_process.wait()
        
    except KeyboardInterrupt:
        print("\n Stopping application...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()

        print("Application stopped")
