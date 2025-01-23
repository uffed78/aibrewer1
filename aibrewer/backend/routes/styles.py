import json
import os
from flask import Blueprint, jsonify, request
from routes.filters import filter_styles
from backend.gpt_integration import generate_recipe_with_gpt

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
    try:
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

        # Debug: Skriv ut parametrarna för att säkerställa att de tas emot korrekt
        print("Filter parameters:", {
            "category": category,
            "abv_min": abv_min, "abv_max": abv_max,
            "ibu_min": ibu_min, "ibu_max": ibu_max,
            "srm_min": srm_min, "srm_max": srm_max,
            "og_min": og_min, "og_max": og_max,
            "fg_min": fg_min, "fg_max": fg_max,
        })

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

        return jsonify(filtered_styles), 200

    except Exception as e:
        print("Error in /styles/filter:", str(e))  # Debug: Skriv ut felet
        return jsonify({"error": str(e)}), 500


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

# Existing route to fetch beer styles
@styles_bp.route('/styles/select', methods=['POST'])
def select_style_and_generate():
    """
    Filters beer styles based on provided parameters and interacts with GPT for further recipe customization.
    """
    try:
        # Get filter parameters from request
        filters = request.json.get('filters', {})
        selected_style_name = request.json.get('selected_style', None)

        # Load beer styles from existing JSON
        beer_styles = load_beer_styles()

        # If no style is selected, filter the styles based on parameters
        if not selected_style_name:
            filtered_styles = filter_styles(
                beer_styles,
                category=filters.get('category'),
                abv_min=filters.get('abv_min', 0),
                abv_max=filters.get('abv_max', 100),
                ibu_min=filters.get('ibu_min', 0),
                ibu_max=filters.get('ibu_max', 1000),
                srm_min=filters.get('srm_min', 0),
                srm_max=filters.get('srm_max', 100),
                og_min=filters.get('og_min', 0),
                og_max=filters.get('og_max', 2),
                fg_min=filters.get('fg_min', 0),
                fg_max=filters.get('fg_max', 2)
            )
            return jsonify({"filtered_styles": filtered_styles}), 200

        # If a style is selected, send it to GPT
        selected_style = next((s for s in beer_styles if s["name"] == selected_style_name), None)
        if not selected_style:
            return jsonify({"error": "Selected style not found"}), 404

        # Generate a recipe with GPT using the selected style
        gpt_prompt = (
            f"Based on the style '{selected_style_name}', generate a beer recipe."
        )
        gpt_response = generate_recipe_with_gpt(gpt_prompt)
        return jsonify({"style": selected_style, "gpt_response": gpt_response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def load_beer_styles():
    """
    Utility function to load beer styles from the JSON file.
    """
    file_path = os.path.join(os.path.dirname(__file__), "../bjcp_styles.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
