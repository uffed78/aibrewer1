import os
from flask import Blueprint, jsonify, request, send_from_directory
from backend.brewfather_api import get_all_inventory
from backend.gpt_integration import generate_recipe_with_gpt, continue_gpt_conversation, save_recipe_to_file
from backend.gpt_integration import get_system_instruction
from backend.equipment_profiles import get_equipment_profile

function_a_bp = Blueprint('function_a', __name__)

@function_a_bp.route('/generate-from-inventory', methods=['POST'])
def generate_from_inventory():
    try:
        user_selected_ingredients = request.json.get('ingredients', [])
        selected_profile = request.json.get('profile', "Grainfather G30")  # Standardprofil

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

        return jsonify({
            "style_suggestions": gpt_response
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500





@function_a_bp.route('/continue-discussion', methods=['POST'])
def continue_discussion():
    try:
        messages = request.json.get('messages', [])
        ingredients = request.json.get('ingredients', [])
        selected_profile = request.json.get('profile', "Grainfather G30")

        if not messages:
            return jsonify({"error": "No conversation history provided"}), 400
        
        # Hämta bryggverksprofil
        equipment_data = get_equipment_profile(selected_profile)
        if not equipment_data:
            return jsonify({"error": "Invalid equipment profile"}), 400

        # Lägg till systemmeddelande om det inte redan finns
        if not any(msg['role'] == 'system' for msg in messages):
            messages.insert(0, get_system_instruction())

        # Lägg till bryggverksprofil och ingredienser i historiken
        messages.insert(0, {
            "role": "system",
            "content": f"Ingredienser i inventarielistan: {ingredients}\n\nUtrustningsprofil:\n{equipment_data['xml']}"
        })

        # Skicka historik till GPT
        gpt_response = continue_gpt_conversation(messages)

        if isinstance(gpt_response, dict) and 'error' in gpt_response:
            return jsonify({"error": gpt_response['error']}), 500

        return jsonify({"gpt_response": gpt_response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500








@function_a_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Serve the generated BeerXML file for download."""
    directory = os.path.join(os.getcwd(), 'data')  # Relativ sökväg till 'data'-mappen
    try:
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@function_a_bp.route('/generate-beerxml', methods=['POST'])
def generate_beerxml():
    try:
        data = request.get_json()
        ingredients = data.get('ingredients', [])
        selected_style = data.get('style', "Custom Ale")
        selected_profile = data.get('profile', "Grainfather G30")
        messages = data.get('messages', [])

        if not ingredients:
            return jsonify({"error": "No ingredients provided"}), 400

        # Hämta bryggverksprofil
        equipment_data = get_equipment_profile(selected_profile)
        if not equipment_data:
            return jsonify({"error": "Invalid equipment profile"}), 400

        # Skapa GPT-prompt
        gpt_prompt = f"{get_system_instruction()['content']}\n\n"
        gpt_prompt += "Generate a BeerXML recipe optimized for the specified brewing equipment.\n\n"
        gpt_prompt += "### Equipment Profile:\n"
        gpt_prompt += f"{equipment_data['xml']}\n\n"
        gpt_prompt += "### Brewing Parameters:\n"
        gpt_prompt += f"- Batch Size: {equipment_data['params']['batch_size']} L\n"
        gpt_prompt += f"- Boil Size: {equipment_data['params']['boil_size']} L\n"
        gpt_prompt += f"- Boil Time: {equipment_data['params']['boil_time']} min\n"
        gpt_prompt += f"- Efficiency: {equipment_data['params']['efficiency']}%\n"
        gpt_prompt += f"- Evaporation Rate: {equipment_data['params']['evap_rate']}%\n"
        gpt_prompt += f"- Trub Chiller Loss: {equipment_data['params']['trub_loss']} L\n"
        gpt_prompt += f"- Lauter Deadspace: {equipment_data['params']['deadspace']} L\n\n"

        gpt_prompt += "### Available Ingredients:\n"
        gpt_prompt += f"{ingredients}\n\n"
        gpt_prompt += "### Target Beer Style:\n"
        gpt_prompt += f"{selected_style}\n\n"
        gpt_prompt += "### Conversation History:\n"

        for message in messages:
            gpt_prompt += f"{message['role'].capitalize()}: {message['content']}\n"

        print("DEBUG: GPT Prompt:", gpt_prompt)


        # Generera BeerXML
        gpt_response = generate_recipe_with_gpt(gpt_prompt)

        if isinstance(gpt_response, dict) and 'error' in gpt_response:
            return jsonify({"error": gpt_response['error']}), 500

        # Spara filen
        file_path = os.path.join(os.getcwd(), 'data', 'generated_recipe.xml')

        with open(file_path, 'w') as file:
            file.write(gpt_response)

        return jsonify({
            "file_path": file_path
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




