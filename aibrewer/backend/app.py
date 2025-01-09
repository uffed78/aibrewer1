import sys
import os
from flask import Flask

# Lägg till roten för projektet i sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from routes.inventory import inventory_bp
from routes.recipes import recipes_bp
from routes.styles import styles_bp
from routes.frontend import frontend_bp

app = Flask(__name__)

# Registrera Blueprints
app.register_blueprint(inventory_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(styles_bp)
app.register_blueprint(frontend_bp)

# Health Check Route
@app.route('/status', methods=['GET'])
def status():
    return {"status": "API is running"}

if __name__ == '__main__':
    app.run(debug=True)
