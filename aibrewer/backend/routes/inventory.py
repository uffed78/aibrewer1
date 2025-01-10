from flask import Blueprint, jsonify, request
from backend.brewfather_api import get_inventory, get_all_inventory, get_inventory_item

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

@inventory_bp.route('/inventory/all', methods=['GET'])
def all_inventory():
    """
    Endpoint för att hämta alla kategorier av inventarier från Brewfather.
    """
    data = get_all_inventory()
    if "error" in data:
        return jsonify(data), 500
    return jsonify(data)

@inventory_bp.route('/inventory/<category>/<item_id>', methods=['GET'])
def inventory_item(category, item_id):
    """
    Endpoint för att hämta en specifik ingrediens baserat på kategori och ID.
    """
    data = get_inventory_item(category, item_id)
    if "error" in data:
        return jsonify(data), 500
    return jsonify(data)
