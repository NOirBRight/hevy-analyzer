"""
Launcher script for Hevy Data Analyzer
This script starts the Streamlit app when running as an executable.
"""
import sys
import os
import webbrowser
import threading
import time
from streamlit.web import cli as stcli

def open_browser():
    """Wait for server to start, then open browser."""
    time.sleep(2)  # Wait for Streamlit to start
    webbrowser.open('http://localhost:8501')

def main():
    # Get the directory where the executable/script is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to app directory
    os.chdir(app_dir)
    
    # Path to the main app
    app_path = os.path.join(app_dir, "app.py")
    
    # Open browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run streamlit
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false",
        "--server.port=8501",
    ]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
