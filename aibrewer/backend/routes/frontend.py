from flask import Blueprint, send_from_directory, current_app
import os

frontend_bp = Blueprint('frontend', __name__)

# Route för att servera index.html (eller specifika frontendfiler)
@frontend_bp.route('/<path:filename>')
def static_files(filename):
    # Dynamisk sökväg till frontend-mappen, anpassad till projektstrukturen
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend'))
    return send_from_directory(frontend_path, filename)

# Route för att servera en standardfil om ingen specifik anges (index.html)
@frontend_bp.route('/')
def index():
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend'))
    return send_from_directory(frontend_path, 'index.html')
