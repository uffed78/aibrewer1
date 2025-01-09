import json
import os
from flask import Blueprint, jsonify, request
from routes.filters import filter_styles

styles_bp = Blueprint('styles', __name__)  # Blueprint definieras här

# Dynamisk sökväg för JSON-filen
file_path = os.path.join(os.path.dirname(__file__), "../bjcp_styles.json")

# Ladda datan från JSON-filen
with open(file_path, 'r', encoding='utf-8') as f:  # Lägg till encoding='utf-8'
    beer_styles = json.load(f)

@styles_bp.route('/styles', methods=['GET'])
def get_all_styles():
    """
    Returnerar en lista över alla ölstilar med grundläggande information.
    """
    return jsonify([{
        "name": style["name"],
        "number": style["number"],
        "category": style["category"]
    } for style in beer_styles])

@styles_bp.route('/styles/filter', methods=['GET'])
def filter_styles_route():
    """
    Filtrerar ölstilar baserat på attribut som kategori, ABV, IBU, SRM, OG, FG.
    Exempel: /styles/filter?abv_min=4.5&abv_max=6.5&category=Amber
    """
    # Hämta filterparametrar
    category = request.args.get('category')
    abv_min = float(request.args.get('abv_min', 0))
    abv_max = float(request.args.get('abv_max', 100))
    ibu_min = float(request.args.get('ibu_min', 0))
    ibu_max = float(request.args.get('ibu_max', 1000))
    srm_min = float(request.args.get('srm_min', 0))
    srm_max = float(request.args.get('srm_max', 100))
    og_min = float(request.args.get('og_min', 0))
    og_max = float(request.args.get('og_max', 2))
    fg_min = float(request.args.get('fg_min', 0))
    fg_max = float(request.args.get('fg_max', 2))

    # Anropa filterfunktionen
    filtered_styles = filter_styles(
        beer_styles,
        category=category,
        abv_min=abv_min,
        abv_max=abv_max,
        ibu_min=ibu_min,
        ibu_max=ibu_max,
        srm_min=srm_min,
        srm_max=srm_max,
        og_min=og_min,
        og_max=og_max,
        fg_min=fg_min,
        fg_max=fg_max
    )

    return jsonify(filtered_styles)

@styles_bp.route('/styles/<style_number>', methods=['GET'])
def get_style_by_number(style_number):
    """
    Returnerar detaljerad information om en specifik stil baserat på dess nummer.
    """
    style = next((s for s in beer_styles if s["number"] == style_number), None)
    if style:
        return jsonify(style)
    else:
        return jsonify({"error": "Style not found"}), 404

@styles_bp.route('/styles/categories', methods=['GET'])
def get_categories():
    """
    Returnerar en lista över alla unika kategorier för frontend-rullista.
    """
    categories = list(set(style.get("category", "") for style in beer_styles))
    return jsonify(categories)
