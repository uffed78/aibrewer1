from flask import Blueprint, jsonify, request
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

# 2️⃣ GPT Genererar receptutkast
@function_a_v2_bp.route('/generate-draft', methods=['POST'])
def generate_draft():
    data = request.json
    style = data.get('style')
    ingredients = data.get('ingredients', [])
    profile = data.get('profile', "Grainfather G30")

    gpt_prompt = f"""
    Skapa ett receptutkast för {style} med:
    {ingredients}
    
    Inkludera:
    - Maltfördelning i %
    - Humletyper och tillsättningstider
    - Jästtyp
    - Målvärden (OG, FG, IBU, EBC)
    """
    
    draft = generate_recipe_with_gpt(gpt_prompt)
    return jsonify({"draft": draft})

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
    
    # Utför beräkningar
    calculated = {
        "og": calculate_og(recipe_draft, equipment),
        "ibu": calculate_ibu(recipe_draft, equipment),
        "ebc": calculate_ebc(recipe_draft, equipment),
        "abv": None  # Beräknas senare
    }
    
    return jsonify({"calculated": calculated})

# 4️⃣ Backend genererar BeerXML
@function_a_v2_bp.route('/generate-xml', methods=['POST'])
def generate_xml():
    data = request.json
    recipe_draft = data.get('draft')
    calculated = data.get('calculated')
    profile = data.get('profile', "Grainfather G30")
    
    equipment = get_equipment_profile(profile)
    
    beer_xml = generate_beerxml(
        recipe_draft, 
        calculated,
        equipment
    )
    
    return jsonify({"beerxml": beer_xml})

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