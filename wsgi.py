import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app
from aibrewer.backend.app import app

if __name__ == "__main__":
    app.run()
