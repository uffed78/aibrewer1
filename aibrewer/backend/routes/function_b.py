# /backend/routes/function_b.py

from flask import Blueprint, jsonify, request, current_app
import json
import os
import traceback
# Fix imports to use absolute paths
from aibrewer.backend.brewfather_api import get_inventory, get_all_inventory, get_inventory_item

# Skapa Blueprint för funktion b
function_b_bp = Blueprint('function_b', __name__)

@function_b_bp.route('/inventory', methods=['GET'])
def inventory():
    """
    Endpoint för att hämta inventarier från Brewfather API.
    Accepterar en 'category' parameter (fermentables, hops, yeasts, miscs).
    """
    category = request.args.get('category', 'fermentables')  # Standard till fermentables
    data = get_inventory(category)
    return jsonify(data)

@function_b_bp.route('/inventory/all', methods=['GET', 'POST'])
def all_inventory():
    """
    Endpoint för att hämta alla kategorier av inventarier med positivt saldo.
    Now supports both GET and POST methods for more flexibility.
    """
    try:
        # Get API credentials from request if POST, otherwise from environment
        if request.method == 'POST':
            data = request.get_json()
            api_id = data.get('apiId')
            api_key = data.get('apiKey')
        else:
            # Default to environment variables for GET requests
            from os import environ
            api_id = environ.get('BREWFATHER_USERID')
            api_key = environ.get('BREWFATHER_APIKEY')
            
        # Validate API credentials
        if not api_id or not api_key:
            return jsonify({
                "error": "API ID and API Key required",
                "detail": "Please provide Brewfather API credentials"
            }), 400
            
        # Try to get inventory
        data = get_all_inventory(api_id=api_id, api_key=api_key)
        return jsonify(data), 200
        
    except Exception as e:
        # Capture and return detailed error information
        error_message = str(e)
        stack_trace = traceback.format_exc()
        current_app.logger.error(f"Inventory fetch error: {error_message}\n{stack_trace}")
        
        return jsonify({
            "error": "Failed to fetch inventory",
            "detail": error_message,




















        return jsonify({"error": str(e)}), 500    except Exception as e:        })            }                "yeasts": [{"name": "Test Yeast", "inventory": 2}]                "hops": [{"name": "Test Hop", "inventory": 100}],                "fermentables": [{"name": "Test Malt", "inventory": 5}],            "mock_data": {            "message": "Test endpoint working",            "status": "success",        return jsonify({        # Return a minimal test response    try:    """    Debug endpoint for testing inventory functionality without API keys.    """def test_inventory():@function_b_bp.route('/inventory/test', methods=['GET'])        }), 500            "suggestion": "Check your API credentials and network connection"
        }), 500







    return jsonify(data)        return jsonify(data), 500    if "error" in data:    data = get_inventory_item(category, item_id)@function_b_bp.route('/inventory/<category>/<item_id>', methods=['GET'])
def inventory_item(category, item_id):
    """
    Endpoint för att hämta en specifik ingrediens baserat på kategori och ID.
    """