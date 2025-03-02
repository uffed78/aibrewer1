import sys
import os
from flask import Flask, send_from_directory
from flask_cors import CORS

# Add the parent directory to sys.path to make relative imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Update imports to use absolute paths
from aibrewer.backend.routes.frontend import frontend_bp
from aibrewer.backend.routes.function_b import function_b_bp
from aibrewer.backend.routes.function_c import function_c_bp
from aibrewer.backend.routes.function_a_v2 import function_a_v2_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Increase server timeout and max request size
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB max response size

# Register Blueprints
app.register_blueprint(frontend_bp)
app.register_blueprint(function_b_bp, url_prefix='/function_b')
app.register_blueprint(function_c_bp, url_prefix='/function_c')
app.register_blueprint(function_a_v2_bp, url_prefix='/function_a_v2')

# Health Check Route
@app.route('/status', methods=['GET'])
def status():
    return {"status": "API is running"}

@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

# Modified to better handle production environment
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)