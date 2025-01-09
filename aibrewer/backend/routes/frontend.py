from flask import Blueprint, send_from_directory
import os

frontend_bp = Blueprint('frontend', __name__)

# Route för att servera index.html
@frontend_bp.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

# Route för att servera CSS och JavaScript
@frontend_bp.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('../frontend', filename)
