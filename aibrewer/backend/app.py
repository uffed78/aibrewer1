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

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Öka serverns timeout och maxstorlek på begäran
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # För att förbättra prestanda på JSON-svar
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB maxstorlek för svaret

# Registrera Blueprints

app.register_blueprint(frontend_bp)
app.register_blueprint(function_b_bp, url_prefix='/function_b')
app.register_blueprint(function_c_bp, url_prefix='/function_c')
app.register_blueprint(function_a_v2_bp, url_prefix='/function_a_v2')

# Health Check Route
@app.route('/status', methods=['GET'])
def status():
    return {"status": "API is running"}

# Nytt här under

@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)