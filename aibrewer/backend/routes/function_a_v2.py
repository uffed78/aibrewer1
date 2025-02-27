import io
import json
from flask import Blueprint, jsonify, request, send_file
from backend.gpt_integration import generate_recipe_with_gpt, continue_gpt_conversation
from backend.equipment_profiles import get_equipment_profile
from backend.recipe_calculations import (
    validate_recipe_draft,
    calculate_ibu,
    calculate_og,
    calculate_ebc,
    generate_beerxml
)
from backend.brewfather_api import get_all_inventory

function_a_v2_bp = Blueprint('function_a_v2', __name__)

# 1️⃣ GPT Föreslår ölstilar
@function_a_v2_bp.route('/suggest-styles', methods=['POST'])
def suggest_styles():
    data = request.json
    ingredients = data.get('ingredients', [])
    profile = data.get('profile', "Grainfather G30")
    
    equipment = get_equipment_profile(profile)
    gpt_prompt = f"""
    Föreslå 3-5 ölstilar som kan bryggas med dessa ingredienser:
    {ingredients}
    
    Utrustningsbegränsningar:
    - Max kokvolym: {equipment['params']['boil_size']}L
    - Effektivitet: {equipment['params']['efficiency']}%
    """
    
    styles = generate_recipe_with_gpt(gpt_prompt)
    return jsonify({"styles": styles})

def srm_to_lovibond(srm: float) -> float:
    """
    Konverterar SRM till Lovibond.
    Formula: °L = (SRM + 0.76) / 1.3546
    """
    return (srm + 0.76) / 1.3546

# 2️⃣ GPT Genererar receptutkast

@function_a_v2_bp.route('/generate-draft', methods=['POST'])
def generate_draft():
    data = request.json
    style = data.get('style', "")
    ingredients = data.get('ingredients', [])
    profile = data.get('profile', "Grainfather G30")
    
    # Get API credentials
    api_id = data.get('apiId')
    api_key = data.get('apiKey')
    
    # Sanitize style name to avoid potential issues with special characters
    style = style.strip()
    
    # Get inventory metadata from request instead of making a new API call
    inventory_data = data.get('inventory_data')
    
    # Only fetch from Brewfather if inventory data wasn't provided
    if not inventory_data:
        if not api_id or not api_key:
            from os import getenv
            api_id = getenv("BREWFATHER_USERID")
            api_key = getenv("BREWFATHER_APIKEY")
            
        if api_id and api_key:
            try:
                inventory_data = get_all_inventory(api_id=api_id, api_key=api_key)
            except Exception as e:
                # Continue with default values if API call fails
                print(f"Warning: Failed to get inventory: {str(e)}")
                inventory_data = {"fermentables": [], "hops": [], "yeasts": []}
        else:
            inventory_data = {"fermentables": [], "hops": [], "yeasts": []}
    
    equipment = get_equipment_profile(profile)
    
    fermentables_map = {f["name"].lower(): f for f in inventory_data.get("fermentables", [])}
    hops_map = {h["name"].lower(): h for h in inventory_data.get("hops", [])}
    yeasts_map = {y["name"].lower(): y for y in inventory_data.get("yeasts", [])}
    
    try:
        # Create a nicely formatted list of ingredients for the prompt
        formatted_ingredients = ""
        for ing in ingredients:
            formatted_ingredients += f"- {ing.get('name', '')} ({ing.get('category', '')})\n"
        
        gpt_prompt = f"""
        Skapa ett ölrecept i JSON-format för en {style} med följande ingredienser:
        {formatted_ingredients}

        Bryggverkets begränsningar:
        - Maximal kokvolym: {equipment['params']['boil_size']}L
        - Bryggverkets effektivitet: {equipment['params']['efficiency']}%

        Se till att receptförslagen är stiltypiska enligt bjpc 2021.

        Svara **endast** med ett JSON-objekt, inget annat. Inkludera följande fält:
        {{
            "name": "Receptnamn",
            "target_og": 1.045,  
            "fermentables": {{
                "Maltnamn": [procent, potential_sg]  
            }},
            "hops": [
                {{
                    "name": "Humlenamn",
                    "alpha": alpha_procent,
                    "time": koktid,
                    "ibu_contribution": önskad_ibu
                }}
            ],
            "yeast": {{
                "type": "Jästnamn",
                "amount": antal_förpackningar
            }}
        }}
        """

        draft = generate_recipe_with_gpt(gpt_prompt)
        
        # Try to extract JSON from GPT response if it's not pure JSON
        draft_text = draft.strip()
        if not (draft_text.startswith("{") and draft_text.endswith("}")):
            # Try to find JSON object in response
            import re
            json_match = re.search(r'\{[\s\S]*\}', draft_text)
            if json_match:
                draft_text = json_match.group(0)
            else:
                return jsonify({
                    "error": "Could not extract valid JSON from GPT response",
                    "raw_response": draft
                }), 400
        
        draft_json = json.loads(draft_text)
        
        # Spara originalformatet för fermentables för beräkningar
        calculation_fermentables = draft_json["fermentables"].copy()
        
        # Skapa den berikade versionen för metadata
        enriched_data = {
            "fermentables_metadata": {},
            "fermentables": calculation_fermentables  # Behåll originalformatet för beräkningar
        }

        # Berika metadata separat
        for malt_name, values in draft_json["fermentables"].items():
            malt_data = fermentables_map.get(malt_name.lower())
            if malt_data:
                srm_color = malt_data.get("color", 0)
                
                enriched_data["fermentables_metadata"][malt_name] = {
                    "_id": malt_data.get("_id"),
                    "potentialPercentage": malt_data.get("potentialPercentage"),
                    "color": srm_color,
                    "srm_color": srm_color,
                    "supplier": malt_data.get("supplier"),
                    "origin": malt_data.get("origin"),
                    "type": malt_data.get("type", "Grain"),
                    "notFermentable": malt_data.get("notFermentable", False)
                }
            else:
                enriched_data["fermentables_metadata"][malt_name] = {
                    "_id": f"default-{malt_name.lower().replace(' ', '-')}",
                    "potentialPercentage": 75,
                    "color": 0,
                    "srm_color": 0,
                    "type": "Grain"
                }

        # Uppdatera draft_json med den nya strukturen
        draft_json.update(enriched_data)

        # Beräkna post-boil volume
        post_boil_volume = (equipment["params"]["boil_size"] - 
                        (equipment["params"]["boil_size"] * 
                        (equipment["params"]["evap_rate"] / 100.0) * 
                        (equipment["params"]["boil_time"] / 60.0))) * 0.96

        # Beräkna OG, IBU och EBC
        og_result = calculate_og(draft_json, equipment)
        ibu_result = calculate_ibu(draft_json, equipment, post_boil_volume)
        ebc_result = calculate_ebc(draft_json, og_result["fermentables"], post_boil_volume)

        # Lägg till de beräknade värdena i draft_json
        draft_json["og"] = og_result["og"]
        draft_json["ibu"] = ibu_result[0]  # Total IBU
        draft_json["ebc"] = ebc_result

        return jsonify({"draft": draft_json})
        
    except json.JSONDecodeError:
        return jsonify({
            "error": "GPT response is not valid JSON", 
            "raw_response": draft
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"Error processing draft: {str(e)}", 
            "raw_response": draft
        }), 500

# 3️⃣ Backend validerar och beräknar
@function_a_v2_bp.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    recipe_draft = data.get('draft')
    profile = data.get('profile', "Grainfather G30")
    
    # Validera GPT:s utkast
    validation_result = validate_recipe_draft(recipe_draft)
    if not validation_result["valid"]:
        return jsonify({"error": validation_result["message"]}), 400
    
    # Hämta utrustningsdata
    equipment = get_equipment_profile(profile)

    # Beräkna post-boil volume
    post_boil_volume = (equipment["params"]["boil_size"] - 
                        (equipment["params"]["boil_size"] * (equipment["params"]["evap_rate"] / 100.0) * 
                        (equipment["params"]["boil_time"] / 60.0))) * 0.96
    
    # Beräkna OG och maltvikt
    og_result = calculate_og(recipe_draft, equipment)

    # Utför beräkningar
    calculated = {
        "og": og_result["og"],        
        "ibu": calculate_ibu(recipe_draft, equipment, post_boil_volume),
        "ebc": calculate_ebc(recipe_draft, og_result["fermentables"], post_boil_volume),
        "fermentables": og_result["fermentables"],
        "abv": None  # Beräknas senare        
    }
    
    return jsonify({"calculated": calculated})

# 4️⃣ Backend genererar BeerXML
@function_a_v2_bp.route('/generate-xml', methods=['POST'])
def generate_xml():
    try:
        data = request.json
        draft = data.get('draft')
        calculated = data.get('calculated', {})
        profile = data.get('profile', "Grainfather G30")
        
        # Get API credentials 
        api_id = data.get('apiId')
        api_key = data.get('apiKey')
        
        if not api_id or not api_key:
            return jsonify({"error": "API ID och API Key krävs"}), 400
            
        # Use the provided credentials to get inventory data
        inventory_data = get_all_inventory(api_id=api_id, api_key=api_key)

        # Debug logging
        print("DEBUG: Received draft:", json.dumps(draft, indent=2))
        print("DEBUG: Received calculated:", json.dumps(calculated, indent=2))
        print("DEBUG: Using API credentials for Brewfather")

        # Get equipment profile
        equipment = get_equipment_profile(profile)

        # Calculate post-boil volume
        post_boil_volume = (equipment["params"]["boil_size"] - 
                          (equipment["params"]["boil_size"] * 
                           (equipment["params"]["evap_rate"] / 100.0) * 
                           (equipment["params"]["boil_time"] / 60.0))) * 0.96

        # Match fermentables with inventory data
        fermentables_data = []
        for malt_name in calculated.get("fermentables", {}):
            # Look for exact match first
            malt_data = next(
                (f for f in inventory_data.get("fermentables", []) 
                 if f["name"].lower() == malt_name.lower()),
                None
            )
            # If no exact match, try partial match
            if not malt_data:
                malt_data = next(
                    (f for f in inventory_data.get("fermentables", [])
                     if malt_name.lower() in f["name"].lower()),
                    {"name": malt_name, "_id": f"default-{malt_name.lower().replace(' ', '-')}"}
                )
            
            fermentables_data.append(malt_data)

        # Match hops with inventory data
        hops_data = []
        for hop in calculated.get("ibu", [[], []])[1]:
            hop_name = hop["name"]
            # Look for exact match first
            hop_data = next(
                (h for h in inventory_data.get("hops", [])
                 if h["name"].lower() == hop_name.lower()),
                None
            )
            # If no exact match, try partial match
            if not hop_data:
                hop_data = next(
                    (h for h in inventory_data.get("hops", [])
                     if hop_name.lower() in h["name"].lower()),
                    {"name": hop_name, "_id": f"default-{hop_name.lower().replace(' ', '-')}"}
                )
            
            hops_data.append(hop_data)

        # Match yeast with inventory data
        yeast_type = draft.get("yeast", {}).get("type", "")
        yeast_data = next(
            (y for y in inventory_data.get("yeasts", [])
             if y["name"].lower() == yeast_type.lower()),
            next(
                (y for y in inventory_data.get("yeasts", [])
                 if yeast_type.lower() in y["name"].lower()),
                {"name": yeast_type, "_id": f"default-{yeast_type.lower().replace(' ', '-')}"}
            )
        )

        # Update draft with matched ingredient data
        enriched_draft = {
            **draft,
            "fermentables_data": fermentables_data,
            "hops_data": hops_data,
            "yeast": {
                **draft.get("yeast", {}),
                **yeast_data
            }
        }

        # Add style information if not present
        if "style" not in enriched_draft:
            enriched_draft["style"] = {
                "name": "Custom Style",
                "category": "Custom Beer",
                "category_number": "99",
                "style_letter": "X",
                "style_guide": "BJCP 2021"
            }

        # Add default mash profile if not present
        if "mash" not in enriched_draft:
            enriched_draft["mash"] = {
                "grain_temp": 20,
                "steps": [
                    {
                        "name": "Saccharification",
                        "type": "Temperature",
                        "temp": 65,
                        "time": 60
                    }
                ]
            }

        # Do all necessary calculations
        og_result = calculate_og(enriched_draft, equipment)
        ibu_result = calculate_ibu(enriched_draft, equipment, post_boil_volume)
        
        # Update calculated values
        calculated = {
            "og": og_result["og"],
            "fermentables": og_result["fermentables"],
            "ibu": ibu_result,
            "ebc": calculate_ebc(enriched_draft, og_result["fermentables"], post_boil_volume)        
        }

        # Generate XML
        beer_xml = generate_beerxml(enriched_draft, calculated, equipment)
        
        # Create in-memory file
        xml_file = io.BytesIO(beer_xml.encode('utf-8'))
        
        # Generate filename
        recipe_name = enriched_draft.get('name', 'recipe').replace(' ', '_').lower()
        filename = f"{recipe_name}.xml"
        
        return send_file(
            xml_file,
            mimetype='application/xml',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"ERROR in generate-xml: {str(e)}")
        print(f"DEBUG: Current draft state: {json.dumps(draft, indent=2)}")
        print(f"DEBUG: Current calculated state: {json.dumps(calculated, indent=2)}")
        return jsonify({
            "error": str(e),
            "draft": draft,
            "calculated": calculated
        }), 500

# 5️⃣ Iterativ diskussion med GPT
@function_a_v2_bp.route('/discuss', methods=['POST'])
def discuss():
    data = request.json
    messages = data.get('messages', [])
    current_recipe = data.get('recipe')
    
    # Lägg till receptdata i konversationen
    messages.append({
        "role": "system",
        "content": f"Aktuellt recept: {current_recipe}"
    })
    
    response = continue_gpt_conversation(messages)
    return jsonify({"response": response})

@function_a_v2_bp.route('/test-calculations', methods=['POST'])
def test_calculations():
    data = request.json
    draft = data.get("draft")
    profile = data.get("profile", "Grainfather G30")
    equipment = get_equipment_profile(profile)
    
    if not draft or not equipment:
        return jsonify({"error": "Invalid draft or equipment profile"}), 400
    
    # Validera receptutkastet
    validation = validate_recipe_draft(draft)
    if not validation["valid"]:
        return jsonify({"error": validation["message"]}), 400
    
    # Beräkna OG och maltvikt
    og_result = calculate_og(draft, equipment)
    
    # Beräkna post-boil volume på samma sätt som i calculate_og
    boil_time = equipment["params"]["boil_time"]
    boil_size = equipment["params"]["boil_size"]
    evap_rate = equipment["params"]["evap_rate"] / 100.0
    cooling_factor = 0.96
    boil_off_hours = boil_time / 60.0
    boiled_off = boil_size * evap_rate * boil_off_hours
    post_boil_volume = (boil_size - boiled_off) * cooling_factor

    calculated = {
        "og": og_result["og"],
        "ibu": calculate_ibu(draft, equipment, post_boil_volume),
        "ebc": calculate_ebc(draft, og_result["fermentables"], post_boil_volume),
        "fermentables": og_result["fermentables"]
    }
    
    # Generera BeerXML
    beerxml = generate_beerxml(draft, calculated, equipment)
    
    return jsonify({
        "validation": validation,
        "calculated": calculated,
        "beerxml": beerxml
    })

@function_a_v2_bp.route('/get-inventory', methods=['POST'])
def get_inventory_route():
    """
    Hämtar hela inventory från Brewfather baserat på användaruppgifter och returnerar det som JSON.
    """
    data = request.json
    api_id = data.get('apiId')
    api_key = data.get('apiKey')
    
    if not api_id or not api_key:
        return jsonify({"error": "API ID och API Key krävs"}), 400
        
    try:
        inventory = get_all_inventory(api_id=api_id, api_key=api_key)
        return jsonify(inventory)
    except Exception as e:
        return jsonify({"error": f"Kunde inte hämta inventory: {str(e)}"}), 500