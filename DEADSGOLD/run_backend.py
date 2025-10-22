import sys
import os
import uvicorn

# Get the absolute path to the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Add the project root directory to sys.path
# Assuming project root is the same directory as this script
project_root = script_dir
sys.path.insert(0, project_root)

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
