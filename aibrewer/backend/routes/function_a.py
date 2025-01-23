from flask import Blueprint, jsonify, request, send_from_directory
from backend.brewfather_api import get_all_inventory
from backend.gpt_integration import generate_recipe_with_gpt, continue_gpt_conversation, save_recipe_to_file

function_a_bp = Blueprint('function_a', __name__)

@function_a_bp.route('/generate-from-inventory', methods=['POST'])
def generate_from_inventory():
    try:
        # Hämta data från användarens val
        user_selected_ingredients = request.json.get('ingredients', [])

        if not user_selected_ingredients:
            return jsonify({"error": "No ingredients selected"}), 400

        # Skapa GPT-prompt med hela inventariedatan
        gpt_prompt = (
            "Based on the following complete inventory data provided by the user, "
            "suggest either a beer recipe or suitable beer styles, and generate the recipe in BeerXML format. "
            "Generate a BeerXML recipe for the given inventory data. "
            "Output only the BeerXML code and nothing else. Ensure the XML is valid and complete."
            f"Inventory data:\n{user_selected_ingredients}\n"
        )

        print("GPT Prompt:", gpt_prompt)

        gpt_response = generate_recipe_with_gpt(gpt_prompt)
        print("GPT Response:", gpt_response)

        if isinstance(gpt_response, dict) and 'error' in gpt_response:
            return jsonify({"error": gpt_response['error']}), 500

        # Spara innehållet som en fil
        filename = "generated_recipe.xml"  # Du kan anpassa namnet
        save_recipe_to_file(filename, gpt_response)

        return jsonify({
            "gpt_response": gpt_response,
            "download_link": f"http://127.0.0.1:5000/download/{filename}"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@function_a_bp.route('/continue-discussion', methods=['POST'])
def continue_discussion():
    """
    Fortsätter diskussionen med GPT baserat på användarens tidigare meddelanden.
    """
    try:
        # Ta emot historik av konversationen
        messages = request.json.get('messages', [])

        if not messages:
            return jsonify({"error": "No conversation history provided"}), 400

        # Skicka historik till GPT
        gpt_response = continue_gpt_conversation(messages)

        if isinstance(gpt_response, dict) and 'error' in gpt_response:
            return jsonify({"error": gpt_response['error']}), 500

        # Returnera GPT:s svar
        return jsonify({
            "gpt_response": gpt_response
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@function_a_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    directory = os.path.join(os.getcwd(), 'data')  # Lokal katalog
    file_path = os.path.join(directory, filename)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return {"error": "File not found"}, 404
    return send_from_directory(directory, filename, as_attachment=True)




