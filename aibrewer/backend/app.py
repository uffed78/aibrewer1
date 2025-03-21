import sys
import os
from flask import Flask
from flask_cors import CORS

# Lägg till roten för projektet i sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from routes.inventory import inventory_bp
from routes.recipes import recipes_bp
from routes.styles import styles_bp
from routes.frontend import frontend_bp
from routes.function_a import function_a_bp
from routes.function_b import function_b_bp
from routes.function_c import function_c_bp
from routes.function_a_v2 import function_a_v2_bp

app = Flask(__name__)
CORS(app)

# Öka serverns timeout och maxstorlek på begäran
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # För att förbättra prestanda på JSON-svar
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB maxstorlek för svaret

# Registrera Blueprints
app.register_blueprint(inventory_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(styles_bp)
app.register_blueprint(frontend_bp)
app.register_blueprint(function_a_bp, url_prefix='/function_a')
app.register_blueprint(function_b_bp, url_prefix='/function_b')
app.register_blueprint(function_c_bp, url_prefix='/function_c')
app.register_blueprint(function_a_v2_bp, url_prefix='/function_a_v2')

# Health Check Route
@app.route('/status', methods=['GET'])
def status():
    return {"status": "API is running"}

if __name__ == '__main__':
    app.run(debug=True)