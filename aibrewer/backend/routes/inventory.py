from flask import Blueprint, jsonify, request
from backend.brewfather_api import get_inventory

# Skapa en Blueprint för inventarier
inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory', methods=['GET'])
def inventory():
    """
    Endpoint för att hämta inventarier från Brewfather API.
    Accepterar en 'category' parameter (fermentables, hops, yeasts, miscs).
    """
    category = request.args.get('category', 'fermentables')  # Standard till fermentables
    data = get_inventory(category)
    return jsonify(data)
