import math
from typing import Dict, Any

def validate_recipe_draft(draft: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validerar ett receptutkast från GPT för att säkerställa att det är logiskt och körbart.
    
    Args:
        draft (Dict): Ett receptutkast i JSON-format från GPT.
        
    Returns:
        Dict: Ett resultatobjekt med "valid" (bool) och "message" (str).
    """
    errors = []
    
    # 1. Validera maltfördelning
    if "fermentables" not in draft:
        errors.append("Ingen maltfördelning angiven.")
    else:
        total_percentage = 0
        for malt, values in draft["fermentables"].items():
            if isinstance(values, (list, tuple)) and len(values) == 2:
                percentage = values[0]  # Första elementet är procentandelen
                total_percentage += percentage
            else:
                errors.append(f"Ogiltigt format för malt '{malt}'. Förväntad lista/tuple med två element.")
        
        if not math.isclose(total_percentage, 100, abs_tol=0.1):  # Tillåter liten avrundningsskillnad
            errors.append(f"Maltfördelningen summerar till {total_percentage}%, måste vara 100%.")
    
    # 2. Validera humle
    if "hops" not in draft:
        errors.append("Ingen humle angiven.")
    else:
        for hop in draft["hops"]:
            if "time" not in hop or "ibu_contribution" not in hop:
                errors.append("Varje humle måste ha 'time' och 'ibu_contribution' angivna.")
    
    # 3. Validera jäst
    if "yeast" not in draft:
        errors.append("Ingen jäst angiven.")
    elif "type" not in draft["yeast"] or "amount" not in draft["yeast"]:
        errors.append("Jäst måste ha 'type' och 'amount' angivna.")
    
    return {
        "valid": len(errors) == 0,
        "message": "; ".join(errors) if errors else "Receptutkastet är giltigt."
    }


def calculate_og(draft: Dict[str, Any], equipment: Dict[str, Any]) -> Dict[str, Any]:
    target_og = draft.get("target_og", 1.050)
    boil_size = equipment["params"]["boil_size"]  # i liter
    boil_time = equipment["params"]["boil_time"]  # i minuter
    evap_rate = equipment["params"]["evap_rate"] / 100.0  # t.ex. 7.41% → 0.0741
    cooling_factor = 0.96
    efficiency = equipment["params"]["efficiency"] / 100.0

    # 1. Beräkna post-boil volume
    boil_off_hours = boil_time / 60.0
    boiled_off = boil_size * evap_rate * boil_off_hours
    post_boil_volume_liters = (boil_size - boiled_off) * cooling_factor
    post_boil_volume_gallons = post_boil_volume_liters * 0.264172  # liter → gallon

    # 2. Beräkna required GP
    required_gp = (target_og - 1) * post_boil_volume_gallons * 1000

    # 3. Beräkna maltvikt
    fermentables = {}
    total_gp = 0.0

    for malt, (percentage, potential_sg) in draft["fermentables"].items():
        ppg = (potential_sg - 1) * 1000  # Beräkna PPG
        malt_weight_lbs = (percentage / 100.0) * (required_gp / (ppg * efficiency))
        malt_weight_kg = malt_weight_lbs / 2.20462  # Konvertera lbs → kg
        fermentables[malt] = round(malt_weight_kg, 2)
        total_gp += malt_weight_lbs * ppg * efficiency  # Använd lbs för GP-beräkning

    # 4. Beräkna OG
    og = 1 + (total_gp / (post_boil_volume_gallons * 1000))
    
    return {
        "og": round(og, 3),
        "fermentables": fermentables
    }

    


def calculate_malt_weight(percentage, target_og, post_boil_volume, efficiency, potential_sg):
    """Hjälpfunktion för att beräkna maltvikt"""
    required_points = (target_og - 1) * post_boil_volume
    return (percentage / 100.0) * (required_points / ((potential_sg - 1) * efficiency))

def calculate_ibu(draft: Dict[str, Any], equipment: Dict[str, Any], post_boil_volume: float):
    total_ibu = 0.0
    post_boil_gallons = post_boil_volume * 0.264172  # Liter → gallon
    hops_with_amounts = []

    for hop in draft["hops"]:
        alpha = hop["alpha"] / 100.0  # Konvertera till decimalform
        time = hop["time"]
        target_ibu = hop["ibu_contribution"]
        
        # Korrigerad Tinseth utilization formel
        # Bigness factor = 1.65 * 0.000125^(wort gravity - 1)
        bigness_factor = 1.65 * pow(0.000125, 0.050)  # Använder standard 1.050 OG här
        
        # Boil Time factor = (1 - e^(-0.04 * time)) / 4.15
        boil_time_factor = (1 - math.exp(-0.04 * time)) / 4.15
        
        # Total utilization
        utilization = bigness_factor * boil_time_factor
        
        # Beräkna mängd humle i ounces
        amount_oz = (target_ibu * post_boil_gallons) / (alpha * 7489.2 * utilization)  # 7489.2 är en konstant för metrisk konvertering
        amount_g = amount_oz * 28.3495  # Omvandla till gram

        hop_data = {
            "name": hop["name"],
            "alpha": hop["alpha"],
            "time": time,
            "ibu_contribution": target_ibu,
            "calculated_amount": round(amount_g, 1),
            "utilization": round(utilization * 100, 1)  # Procent
        }
        
        hops_with_amounts.append(hop_data)
        total_ibu += target_ibu

    return total_ibu, hops_with_amounts



def calculate_ebc(draft: Dict[str, Any], fermentables: Dict[str, float], post_boil_volume: float) -> float:
    """
    Beräknar EBC med korrekt enhetshantering.
    """
    post_boil_gallons = post_boil_volume * 0.264172  # Liter → gallon
    total_mcu = 0.0

    for malt, weight_kg in fermentables.items():
        lovibond = draft["fermentables"][malt][1]
        weight_lbs = weight_kg * 2.20462  # kg → lbs
        mcu = (lovibond * weight_lbs) / post_boil_gallons
        total_mcu += mcu

    srm = 1.49 * (total_mcu ** 0.69)
    return round(srm * 1.97, 1)  # SRM → EBC

def generate_beerxml(draft: Dict[str, Any], calculated: Dict[str, Any], equipment: Dict[str, Any]) -> str:
    """
    Generates a complete BeerXML file with all necessary ingredient information.
    Maps Brewfather format to BeerXML format correctly.
    
    Args:
        draft: Recipe draft containing ingredient details and metadata
        calculated: Calculated values (OG, IBU, etc.)
        equipment: Equipment profile information
    
    Returns:
        str: Complete BeerXML content
    """
    xml_parts = [
        '<?xml version="1.0" encoding="ISO-8859-1"?>',
        '<RECIPES>',
        '    <RECIPE>',
        f'        <NAME>{draft.get("name", "Custom Recipe")}</NAME>',
        '        <VERSION>1</VERSION>',
        '        <TYPE>All Grain</TYPE>',
        f'        <BREWER>{equipment.get("brewer", "Unknown")}</BREWER>',
        f'        <BATCH_SIZE>{equipment["params"]["batch_size"]}</BATCH_SIZE>',
        f'        <BOIL_SIZE>{equipment["params"]["boil_size"]}</BOIL_SIZE>',
        f'        <BOIL_TIME>{equipment["params"]["boil_time"]}</BOIL_TIME>',
        f'        <EFFICIENCY>{equipment["params"]["efficiency"]}</EFFICIENCY>'
    ]
    
    # Add style information if available
    if "style" in draft:
        xml_parts.extend([
            '        <STYLE>',
            f'            <NAME>{draft["style"].get("name", "Custom Style")}</NAME>',
            f'            <CATEGORY>{draft["style"].get("category", "Custom Beer")}</CATEGORY>',
            f'            <VERSION>1</VERSION>',
            f'            <CATEGORY_NUMBER>{draft["style"].get("category_number", "99")}</CATEGORY_NUMBER>',
            f'            <STYLE_LETTER>{draft["style"].get("style_letter", "X")}</STYLE_LETTER>',
            f'            <STYLE_GUIDE>{draft["style"].get("style_guide", "BJCP 2021")}</STYLE_GUIDE>',
            '        </STYLE>'
        ])

    # Add calculated values
    total_ibu = calculated["ibu"][0] if isinstance(calculated["ibu"], tuple) else calculated["ibu"]
    xml_parts.extend([
        f'        <OG>{calculated["og"]}</OG>',
        f'        <IBU>{total_ibu}</IBU>',
        f'        <EST_COLOR>{calculated["ebc"]}</EST_COLOR>'
    ])

    # Add fermentables section
    xml_parts.append('        <FERMENTABLES>')
    for malt_name, weight in calculated["fermentables"].items():
        # Hämta original malt data för procent och potential_sg
        malt_values = draft["fermentables"].get(malt_name, [0, 1.000])
        # Hämta metadata för malten
        malt_metadata = draft["fermentables_metadata"].get(malt_name, {})
        
        xml_parts.extend([
            '            <FERMENTABLE>',
            f'                <BF_ID>{malt_metadata.get("_id", "")}</BF_ID>',
            f'                <NAME>{malt_name}</NAME>',
            f'                <VERSION>1</VERSION>',
            f'                <TYPE>{malt_metadata.get("type", "Grain")}</TYPE>',
            f'                <AMOUNT>{weight}</AMOUNT>',
            f'                <YIELD>{malt_metadata.get("potentialPercentage", 75)}</YIELD>',
            f'                <COLOR>{malt_metadata.get("color", 0)}</COLOR>',
            f'                <SUPPLIER>{malt_metadata.get("supplier", "")}</SUPPLIER>',
            f'                <ORIGIN>{malt_metadata.get("origin", "")}</ORIGIN>',
            f'                <NOT_FERMENTABLE>{str(malt_metadata.get("notFermentable", False)).lower()}</NOT_FERMENTABLE>',
            '            </FERMENTABLE>'
        ])
    xml_parts.append('        </FERMENTABLES>')

    # Add hops section with correct mapping
    xml_parts.append('        <HOPS>')
    hops_data = calculated["ibu"][1] if isinstance(calculated["ibu"], tuple) else []
    for hop in hops_data:
        hop_metadata = next((h for h in draft.get("hops", []) if h["name"] == hop["name"]), {})
        xml_parts.extend([
            '            <HOP>',
            f'                <BF_ID>{hop_metadata.get("_id", "")}</BF_ID>',
            f'                <NAME>{hop["name"]}</NAME>',
            '                <VERSION>1</VERSION>',
            f'                <ALPHA>{hop["alpha"]}</ALPHA>',
            f'                <AMOUNT>{hop["calculated_amount"] / 1000.0}</AMOUNT>',
            f'                <USE>{hop_metadata.get("use", "Boil")}</USE>',
            f'                <TIME>{hop["time"]}</TIME>',
            f'                <FORM>{hop_metadata.get("form", "Pellet")}</FORM>',
            '            </HOP>'
        ])
    xml_parts.append('        </HOPS>')

    # Add yeast section
    xml_parts.append('        <YEASTS>')
    yeast_data = draft.get("yeast", {})
    xml_parts.extend([
        '            <YEAST>',
        f'                <BF_ID>{yeast_data.get("_id", "default-yeast")}</BF_ID>',
        f'                <NAME>{yeast_data.get("type", "Ale")}</NAME>',
        '                <VERSION>1</VERSION>',
        f'                <TYPE>{yeast_data.get("yeast_type", "Ale")}</TYPE>',
        f'                <FORM>{yeast_data.get("form", "Dry")}</FORM>',
        f'                <AMOUNT>{yeast_data.get("amount", 1)}</AMOUNT>',
        f'                <LABORATORY>{yeast_data.get("laboratory", "")}</LABORATORY>',
        '            </YEAST>'
    ])
    xml_parts.append('        </YEASTS>')

    # Add mash profile
    if "mash" in draft:
        xml_parts.extend([
            '        <MASH>',
            '            <NAME>Default Profile</NAME>',
            '            <VERSION>1</VERSION>',
            f'            <GRAIN_TEMP>{draft["mash"].get("grain_temp", 20)}</GRAIN_TEMP>',
            '            <MASH_STEPS>'
        ])
        for step in draft["mash"].get("steps", []):
            xml_parts.extend([
                '                <MASH_STEP>',
                f'                    <NAME>{step.get("name", "Saccharification")}</NAME>',
                '                    <VERSION>1</VERSION>',
                f'                    <TYPE>{step.get("type", "Temperature")}</TYPE>',
                f'                    <STEP_TEMP>{step.get("temp", 65)}</STEP_TEMP>',
                f'                    <STEP_TIME>{step.get("time", 60)}</STEP_TIME>',
                '                </MASH_STEP>'
            ])
        xml_parts.extend([
            '            </MASH_STEPS>',
            '        </MASH>'
        ])

    # Close the XML structure
    xml_parts.extend([
        '    </RECIPE>',
        '</RECIPES>'
    ])

    return '\n'.join(xml_parts)