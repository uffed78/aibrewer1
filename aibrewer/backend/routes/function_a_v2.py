import os
from flask import Blueprint, jsonify, request, send_from_directory
from backend.brewfather_api import get_all_inventory
from backend.gpt_integration import generate_recipe_with_gpt, continue_gpt_conversation, save_recipe_to_file
from backend.gpt_integration import get_system_instruction
from backend.equipment_profiles import get_equipment_profile
from backend.recipe_calculations import calculate_recipe_values

function_a_v2_bp = Blueprint('function_a_v2', __name__)

# 1️⃣ GPT föreslår ölstilar baserat på inventory
@function_a_v2_bp.route('/suggest-styles', methods=['POST'])
def suggest_styles():
    try:
        user_selected_ingredients = request.json.get('ingredients', [])
        selected_profile = request.json.get('profile', "Grainfather G30")

        if not user_selected_ingredients:
            return jsonify({"error": "No ingredients selected"}), 400

        # Hämta bryggverksprofil
        equipment_data = get_equipment_profile(selected_profile)
        if not equipment_data:
            return jsonify({"error": "Invalid equipment profile"}), 400

        # Skapa GPT-prompt
        gpt_prompt = f"{get_system_instruction()['content']}\n\n"
        gpt_prompt += f"Baserat på följande ingredienser och utrustningsprofil, föreslå tre till fem ölstilar som kan bryggas.\n\n"
        gpt_prompt += f"Ingredienser:\n{user_selected_ingredients}\n\n"
        gpt_prompt += f"Utrustningsprofil:\n{equipment_data['xml']}\n"

        gpt_response = generate_recipe_with_gpt(gpt_prompt)

        if isinstance(gpt_response, dict) and 'error' in gpt_response:
            return jsonify({"error": gpt_response['error']}), 500

        return jsonify({"style_suggestions": gpt_response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 2️⃣ GPT skapar receptstruktur
@function_a_v2_bp.route('/generate-recipe-draft', methods=['POST'])
def generate_recipe_draft():
    try:
        selected_style = request.json.get('style', "Custom Ale")
        user_selected_ingredients = request.json.get('ingredients', [])
        selected_profile = request.json.get('profile', "Grainfather G30")

        if not selected_style or not user_selected_ingredients:
            return jsonify({"error": "Missing style or ingredients"}), 400

        # Skapa GPT-prompt för att skapa receptstruktur
        gpt_prompt = f"{get_system_instruction()['content']}\n\n"
        gpt_prompt += f"Baserat på ölstilen {selected_style} och ingredienserna, skapa en receptstruktur med procentandelar.\n\n"
        gpt_prompt += f"Ingredienser:\n{user_selected_ingredients}\n\n"
        gpt_prompt += f"Utrustningsprofil:\n{get_equipment_profile(selected_profile)['xml']}\n"

        gpt_response = generate_recipe_with_gpt(gpt_prompt)

        if isinstance(gpt_response, dict) and 'error' in gpt_response:
            return jsonify({"error": gpt_response['error']}), 500

        return jsonify({"recipe_draft": gpt_response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 3️⃣ Backend räknar ut värden
@function_a_v2_bp.route('/calculate-recipe', methods=['POST'])
def calculate_recipe():
    try:
        recipe_draft = request.json.get('recipe_draft', {})
        selected_profile = request.json.get('profile', "Grainfather G30")

        if not recipe_draft:
            return jsonify({"error": "No recipe draft provided"}), 400

        calculated_values = calculate_recipe_values(recipe_draft, selected_profile)

        return jsonify({"calculated_recipe": calculated_values}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 4️⃣ Backend genererar BeerXML
@function_a_v2_bp.route('/generate-beerxml-v2', methods=['POST'])
def generate_beerxml_v2():
    try:
        calculated_recipe = request.json.get('calculated_recipe', {})

        if not calculated_recipe:
            return jsonify({"error": "No calculated recipe provided"}), 400

        # Spara filen
        file_path = os.path.join(os.getcwd(), 'data', 'generated_recipe_v2.xml')
        save_recipe_to_file(calculated_recipe, file_path)

        return jsonify({"file_path": file_path}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
