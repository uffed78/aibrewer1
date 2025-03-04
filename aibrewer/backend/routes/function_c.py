# /backend/routes/function_c.py

from flask import Blueprint, jsonify, request
from ..gpt_integration import continue_gpt_conversation, generate_recipe_with_gpt
from .filters import filter_styles
import os
import json
# Fix imports to use relative paths
from ..brewfather_api import get_recipes, get_all_recipes, get_recipe_by_id

# Skapa Blueprint för funktion c
function_c_bp = Blueprint('function_c', __name__)

# Ladda ölstilar från JSON
def load_beer_styles():
    file_path = os.path.join(os.path.dirname(__file__), "../bjcp_styles.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@function_c_bp.route('/styles/select', methods=['POST'])
def select_style_and_generate():
    """
    Filtrerar ölstilar och genererar recept med GPT baserat på användarens val.
    """
    try:
        # Hämta filterparametrar och valt stilnamn från förfrågan
        filters = request.json.get('filters', {})
        selected_style_name = request.json.get('selected_style', None)

        # Ladda alla ölstilar
        beer_styles = load_beer_styles()

        # Om inget stilnamn har valts, filtrera stilar
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

        # Om en stil har valts, skicka det till GPT
        selected_style = next((s for s in beer_styles if s["name"] == selected_style_name), None)
        if not selected_style:
            return jsonify({"error": "Selected style not found"}), 404

        gpt_prompt = f"Based on the style '{selected_style_name}', generate a beer recipe."
        gpt_response = generate_recipe_with_gpt(gpt_prompt)

        return jsonify({"style": selected_style, "gpt_response": gpt_response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@function_c_bp.route('/styles/continue-discussion', methods=['POST'])
def continue_recipe_discussion():
    """
    Fortsätter receptutvecklingen genom att interagera med GPT baserat på användarens meddelanden.
    """
    try:
        messages = request.json.get('messages', [])

        if not messages:
            return jsonify({"error": "No conversation history provided"}), 400

        gpt_response = continue_gpt_conversation(messages)

        if isinstance(gpt_response, dict) and 'error' in gpt_response:
            return jsonify({"error": gpt_response['error']}), 500

        return jsonify({"gpt_response": gpt_response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
