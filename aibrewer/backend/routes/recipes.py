import os
from flask import Blueprint, jsonify, request, send_file
from backend.brewfather_api import get_recipes, get_all_recipes, get_recipe_by_id
from backend.gpt_integration import generate_recipe_with_gpt, continue_gpt_conversation
from backend.brewfather_api import get_all_inventory
from backend.routes.styles import get_all_styles
from backend.gpt_integration import format_recipe_data

# Create a Blueprint for recipe routes
recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/recipes', methods=['GET'])
def recipes():
    """
    Endpoint to fetch recipes from Brewfather API.
    Accepterar filtreringsparametrar via query string.
    """
    filters = request.args.to_dict()  # Hämta alla query-parametrar som en dictionary
    data = get_recipes(filters)
    return jsonify(data)

@recipes_bp.route('/recipes/all', methods=['GET'])
def get_all_user_recipes():
    """
    Hämta alla recept för användaren med fullständig information och stöd för parametrar.
    """
    try:
        from backend.brewfather_api import get_recipes

        # Skapa ett parameterobjekt från inkommande förfrågan
        filters = {
            "complete": request.args.get("complete", "True"),  # Standard till True
            "limit": request.args.get("limit", 50),           # Standard till max 50
            "start_after": request.args.get("start_after", None),
            "order_by": request.args.get("order_by", "_id"),  # Standard till _id
            "order_by_direction": request.args.get("order_by_direction", "asc")  # Standard till stigande ordning
        }

        # Filtrera bort tomma värden från parametrarna
        filters = {k: v for k, v in filters.items() if v is not None}

        # Anropa funktionen med parametrarna
        recipes = get_recipes(filters)

        # Kontrollera och returnera svar
        if isinstance(recipes, dict) and "error" in recipes:
            return jsonify(recipes), 400  # Returnera fel om API-anropet misslyckas
        return jsonify(recipes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@recipes_bp.route('/recipes/<recipe_id>', methods=['GET'])
def recipe_by_id(recipe_id):
    """
    Endpoint för att hämta ett specifikt recept med hjälp av dess _id.
    :param recipe_id: ID för receptet
    """
    data = get_recipe_by_id(recipe_id)
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

@recipes_bp.route('/chat-with-gpt', methods=['POST'])
def chat_with_gpt():
    """
    Endpoint för att hantera GPT-konversation med lagerstatus eller recept.
    """
    try:
        data = request.get_json(force=True)
        messages = data.get('messages', [])
        include_inventory = data.get('include_inventory', False)
        recipe_id = data.get('recipe_id', None)

        # Lägg till lagerstatus om det valts
        if include_inventory:
            inventory_data = get_all_inventory()
            print("Hämtat lagerdata:", inventory_data)  # Debug-utskrift

            # Kontrollera om inventory_data är tomt
            if not inventory_data or not isinstance(inventory_data, dict):
                messages.append({
                    "role": "system",
                    "content": "Ditt lager är tomt eller kunde inte hämtas."
                })
            else:
                # Formatera lagerdatan till en läsbar text
                inventory_text = ""

                if "fermentables" in inventory_data:
                    inventory_text += "Malts:\n" + "\n".join([
                        f"- {item.get('name', 'Okänd')} ({item.get('inventory', '0')} kg)"
                        for item in inventory_data["fermentables"]
                    ]) + "\n"

                if "hops" in inventory_data:
                    inventory_text += "Hops:\n" + "\n".join([
                        f"- {item.get('name', 'Okänd')} ({item.get('inventory', '0')} g, {item.get('alpha', 'N/A')}% alpha)"
                        for item in inventory_data["hops"]
                    ]) + "\n"

                if "yeasts" in inventory_data:
                    inventory_text += "Yeasts:\n" + "\n".join([
                        f"- {item.get('name', 'Okänd')} ({item.get('inventory', '0')} paket, {item.get('attenuation', 'N/A')}% attenuation)"
                        for item in inventory_data["yeasts"]
                    ]) + "\n"

                if "miscs" in inventory_data:
                    inventory_text += "Miscellaneous:\n" + "\n".join([
                        f"- {item.get('name', 'Okänd')} ({item.get('inventory', '0')} {item.get('type', '')})"
                        for item in inventory_data["miscs"]
                    ]) + "\n"

                # Lägg till formaterad lagerdata till GPT-prompt
                messages.append({
                    "role": "system",
                    "content": f"Ditt lager innehåller följande:\n{inventory_text}"
                })

        # Lägg till receptdata om ett recept-ID angivits
        if recipe_id:
            recipe_data = get_recipe_by_id(recipe_id)
            if isinstance(recipe_data, dict) and "error" in recipe_data:
                return jsonify({"error": f"Recept med ID {recipe_id} kunde inte hämtas"}), 404
            messages.append({
                "role": "system",
                "content": f"Recept att utgå från:\n{recipe_data}"
            })

        # Skicka konversationen till GPT
        gpt_response = continue_gpt_conversation(messages)
        print("GPT Response:", gpt_response)  # Debug-utskrift
        return jsonify({"response": gpt_response})
    except Exception as e:
        print("Fel i chat_with_gpt:", str(e))  # Logga felet för debugging
        return jsonify({"error": str(e)}), 500

@recipes_bp.route('/analyze-recipe', methods=['POST'])
def analyze_recipe():
    """
    Endpoint för att analysera och ge förbättringsförslag för ett recept.
    """
    try:
        data = request.get_json(force=True)
        recipe_id = data.get('recipe_id', None)
        recipe_data = data.get('recipe_data', None)
        include_inventory = data.get('include_inventory', False)
        include_styles = data.get('include_styles', False)

        # Hämta receptdata via ID om inget direkt data skickats
        if recipe_id:
            recipe_data = get_recipe_by_id(recipe_id)
            if isinstance(recipe_data, dict) and "error" in recipe_data:
                return jsonify({"error": f"Recept med ID {recipe_id} kunde inte hämtas"}), 404

        if not recipe_data:
            return jsonify({"error": "Ingen receptdata tillhandahållen"}), 400

        inventory_text = ""
        if include_inventory:
            inventory_data = get_all_inventory()
            if "error" in inventory_data:
                inventory_text = "Kunde inte hämta lagerdata."
            else:
                inventory_text = "\n".join([
                    f"- {item.get('name', 'Okänd')} ({item.get('inventory', '0')} {item.get('unit', '')})"
                    for category, items in inventory_data.items() for item in items
                ])

        styles_text = ""
        if include_styles:
            styles = get_all_styles()
            styles_text = "\n".join([
                f"{style['name']}: {style.get('description', 'Ingen beskrivning')}" for style in styles
            ])

        gpt_prompt = f"""
        Receptanalys:
        Recept: {recipe_data}
        
        Lagerstatus:
        {inventory_text}
        
        Stilriktlinjer:
        {styles_text}
        
        Ge förbättringsförslag baserat på receptet, lagret och stilriktlinjerna.
        """

        # Skicka till GPT
        gpt_response = continue_gpt_conversation([{"role": "system", "content": gpt_prompt}])

        # Kontrollera svaret från GPT
        if isinstance(gpt_response, dict) and "error" in gpt_response:
            return jsonify({"error": gpt_response["error"]}), 500

        # Om svaret har 'choices', extrahera innehåll
        if hasattr(gpt_response, "choices") and len(gpt_response.choices) > 0:
            gpt_content = gpt_response.choices[0].message["content"]
        else:
            gpt_content = "GPT kunde inte generera ett svar."

        return jsonify({"response": gpt_content})
    except Exception as e:
        print("Fel i analyze_recipe:", str(e))  # Debug
        return jsonify({"error": str(e)}), 500


@recipes_bp.route('/recipes/improve', methods=['POST'])
def improve_recipe():
    """
    Endpoint för att förbättra ett recept via GPT.
    """
    try:
        data = request.get_json(force=True)
        recipe_id = data.get('recipe_id')

        # Hämta receptdata från Brewfather
        recipe_data = get_recipe_by_id(recipe_id)
        if not recipe_data or "error" in recipe_data:
            return jsonify({"error": f"Recept med ID {recipe_id} kunde inte hämtas"}), 404

        # Skapa prompt
        prompt = (
            "Hej. Här är ett recept på en öl jag hämtat från Brewfather med Brewfathers API-funktion. "
            "Det här är bara ett test, så jag undrar om du kan minska mängden basmalt med tio procent och "
            "sedan ge mig det justerade receptet tillbaka i samma form?\n\n"
            f"{recipe_data}"
        )

        # Skicka prompten till GPT
        messages = [
            {"role": "system", "content": "Du är en erfaren bryggmästare som ger råd och förbättringar på ölrecept."},
            {"role": "user", "content": prompt}
        ]
        gpt_response = continue_gpt_conversation(messages)

        # Kontrollera GPT:s svar
        if not gpt_response or "choices" not in gpt_response:
            return jsonify({"error": "GPT kunde inte generera ett svar."}), 500

        # Extrahera GPT:s svar
        gpt_content = gpt_response['choices'][0]['message']['content']

        # Spara hela svaret som en fil
        file_path = os.path.join(os.getcwd(), "improved_recipe.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(gpt_content)

        # Returnera trunkerat svar och länk till filen
        truncated_content = gpt_content[:2000]  # Returnera de första 2000 tecknen för snabb feedback
        return jsonify({
            "response": truncated_content,
            "full_response_file": "/recipes/improve/download"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recipes_bp.route('/recipes/improve/download', methods=['GET'])
def download_improved_recipe():
    """
    Låt användaren ladda ner hela GPT-svaret som en JSON-fil.
    """
    try:
        file_path = os.path.join(os.getcwd(), "improved_recipe.json")
        if not os.path.exists(file_path):
            return jsonify({"error": "Ingen fil att ladda ner."}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500







