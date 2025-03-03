import sys
import os
import logging, jsonify
from flask import Flask, send_from_directory
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the parent directory to sys.path to make relative imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Update imports to use absolute paths
from aibrewer.backend.routes.frontend import frontend_bp# More specific CORS configuration
from aibrewer.backend.routes.function_b import function_b_bp
from aibrewer.backend.routes.function_c import function_c_bp
from aibrewer.backend.routes.function_a_v2 import function_a_v2_bp
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Add this after creating the Flask app
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB max response size

# Increase server timeout and max request sizes
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB max response sizeblueprint(function_b_bp, url_prefix='/function_b')
rl_prefix='/function_c')
# Register Blueprintsapp.register_blueprint(function_a_v2_bp, url_prefix='/function_a_v2')
app.register_blueprint(frontend_bp)
app.register_blueprint(function_b_bp, url_prefix='/function_b')
app.register_blueprint(function_c_bp, url_prefix='/function_c')
app.register_blueprint(function_a_v2_bp, url_prefix='/function_a_v2')def status():
 is running"}
# Health Check Route
@app.route('/status', methods=['GET'])
def status():def serve_frontend():
    return {"status": "API is running"}ex.html')

@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')










    app.run(host='0.0.0.0', port=port, debug=debug_mode)    debug_mode = os.environ.get('FLASK_ENV') == 'development'    port = int(os.environ.get('PORT', 5001))if __name__ == '__main__':# Modified to better handle production environment    return send_from_directory('../frontend', path)def serve_static(path):@app.route('/<path:path>')
# Add error handlers
@app.errorhandler(500)
def server_error(error):








    app.run(host='0.0.0.0', port=port, debug=debug_mode)    debug_mode = os.environ.get('FLASK_ENV') == 'development'    port = int(os.environ.get('PORT', 5001))if __name__ == '__main__':# Modified to better handle production environment    }), 404        "detail": "The requested resource could not be found"    return jsonify({
        "error": "Internal server error",
        "detail": str(error),
        "suggestion": "Check server logs for more information"
    }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not found",