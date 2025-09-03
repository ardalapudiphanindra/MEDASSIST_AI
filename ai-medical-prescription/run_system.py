#!/usr/bin/env python3
"""
Main runner script for the AI Medical Prescription Verification System.
This script starts both the FastAPI backend and Streamlit frontend.
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import streamlit
        import uvicorn
        print("[OK] All dependencies are installed")
        return True
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def start_backend():
    """Start the FastAPI backend server."""
    backend_dir = Path(__file__).parent / "backend"
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--reload", 
        "--host", "localhost", 
        "--port", "8000"
    ]
    
    print("[INFO] Starting FastAPI backend on http://localhost:8000")
    return subprocess.Popen(cmd, cwd=backend_dir)

def start_frontend():
    """Start the Streamlit frontend."""
    frontend_dir = Path(__file__).parent / "frontend"
    cmd = [
        sys.executable, "-m", "streamlit", 
        "run", "app.py", 
        "--server.port", "8501",
        "--server.address", "localhost"
    ]
    
    print("[INFO] Starting Streamlit frontend on http://localhost:8501")
    return subprocess.Popen(cmd, cwd=frontend_dir)

def main():
    """Main function to start the system."""
    print("AI Medical Prescription Verification System")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Set environment variables
    os.environ["FASTAPI_URL"] = "http://localhost:8000"
    
    # Start services
    backend_process = None
    frontend_process = None
    
    try:
        # Start backend
        backend_process = start_backend()
        time.sleep(3)  # Give backend time to start
        
        # Start frontend
        frontend_process = start_frontend()
        
        print("\n[SUCCESS] System started successfully!")
        print("Backend API: http://localhost:8000")
        print("Frontend UI: http://localhost:8501")
        print("API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop the system")
        
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("[ERROR] Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("[ERROR] Frontend process stopped unexpectedly")
                break
    
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down system...")
    
    finally:
        # Clean up processes
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
        
        print("[SUCCESS] System shutdown complete")

if __name__ == "__main__":
    main()
