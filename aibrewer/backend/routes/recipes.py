from flask import Blueprint, jsonify, request
from backend.brewfather_api import get_recipes  # Vi implementerar denna funktion i nästa steg
from backend.gpt_integration import generate_recipe_with_gpt

# Create a Blueprint for recipe routes
recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/recipes', methods=['GET'])
def recipes():
    """
    Endpoint to fetch recipes from Brewfather API.
    """
    data = get_recipes()
    return jsonify(data)

@recipes_bp.route('/generate-recipe', methods=['POST'])
def generate_recipe_route():
    """
    Endpoint för att generera ett nytt recept med OpenAI:s GPT.
    Förväntar sig en JSON payload med användarens prompt.
    """
    user_prompt = request.json.get('prompt', '')
    if not user_prompt:
        return jsonify({"error": "Prompt is required"}), 400

    gpt_response = generate_recipe_with_gpt(user_prompt)
    return jsonify({"generated_recipe": gpt_response})
