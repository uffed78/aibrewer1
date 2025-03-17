import sys
import os
from flask import Flask, send_from_directory
from flask_cors import CORS

# Add the project root to sys.path to make local imports work
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Now use relative imports for the blueprints
from aibrewer.backend.routes.frontend import frontend_bp
from aibrewer.backend.routes.function_b import function_b_bp
from aibrewer.backend.routes.function_c import function_c_bp
from aibrewer.backend.routes.function_a_v2 import function_a_v2_bp

app = Flask(__name__, static_folder=None)  # Disable default static folder handling

# Print startup message with paths for debugging
print(f"Starting AIBrewer app from {os.path.abspath(os.path.dirname(__file__))}")
print(f"Project root directory: {os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))}")

# Update CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Increase server's timeout and request max size
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB max request size
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development

# Register Blueprints
app.register_blueprint(frontend_bp)
app.register_blueprint(function_b_bp, url_prefix='/function_b')
app.register_blueprint(function_c_bp, url_prefix='/function_c')
app.register_blueprint(function_a_v2_bp, url_prefix='/function_a_v2')

# Define static file routes at the app level
@app.route('/<path:filename>')
def base_static(filename):
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
    print(f"Serving file: {filename} from {frontend_dir}")
    return send_from_directory(frontend_dir, filename)

# Health check route
@app.route('/status')
def status():
    return {"status": "API is running"}

# Root route - serve the main index.html
@app.route('/')
def serve_frontend():
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
    print(f"Serving index.html from {frontend_dir}")
    return send_from_directory(frontend_dir, 'index.html')

if __name__ == '__main__':
    # Använd PORT miljövariabeln som Render.com tillhandahåller
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port)