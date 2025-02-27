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
    """
    Beräknar OG och maltvikter baserat på målvärden och bryggverkets parametrar.
    """
    # Debug equipment parameters
    print(f"DEBUG Equipment params: boil_size={equipment.get('params', {}).get('boil_size', 'N/A')}, " 
          f"evap_rate={equipment.get('params', {}).get('evap_rate', 'N/A')}, "
          f"boil_time={equipment.get('params', {}).get('boil_time', 'N/A')}, "
          f"efficiency={equipment.get('params', {}).get('efficiency', 'N/A')}")
          
    # Debug malt info
    print("DEBUG Malt info:")
    for malt, (percentage, potential_sg) in draft.get("fermentables", {}).items():
        print(f"  - {malt}: {percentage}%, SG={potential_sg}")
    
    target_og = draft.get("target_og", 1.050)
    boil_size = max(0.001, equipment.get('params', {}).get('boil_size', 20))
    evap_rate = max(0, min(100, equipment.get('params', {}).get('evap_rate', 10))) / 100.0
    boil_time = max(0.1, equipment.get('params', {}).get('boil_time', 60))
    cooling_factor = 0.96
    efficiency = max(0.01, equipment.get("params", {}).get("efficiency", 75) / 100.0)

    # 1. Beräkna post-boil volume
    boil_off_hours = boil_time / 60.0
    boiled_off = boil_size * evap_rate * boil_off_hours
    post_boil_volume_liters = max(0.001, (boil_size - boiled_off) * cooling_factor)
    post_boil_volume_gallons = post_boil_volume_liters * 0.264172

    # 2. Beräkna required GP (Gravity Points)
    required_gp = (target_og - 1) * post_boil_volume_gallons * 1000

    # 3. Beräkna maltvikt med exakt procentandelar
    fermentables = {}
    total_weight = 0.0
    temp_weights = {}

    # Först beräkna preliminära vikter
    for malt, (percentage, potential_sg) in draft["fermentables"].items():
        # Ensure potential_sg is valid and not causing division by zero
        potential_sg = max(1.001, float(potential_sg))
        ppg = max(0.1, (potential_sg - 1) * 1000)  # Prevent division by zero
        
        # Prevent division by zero in the calculation
        malt_weight_lbs = (percentage / 100.0) * (required_gp / (ppg * efficiency))
        temp_weights[malt] = malt_weight_lbs
        total_weight += malt_weight_lbs

    # Justera vikterna för att matcha exakta procentandelar
    total_weight = max(0.001, total_weight)  # Ensure non-zero total weight
    for malt, (percentage, _) in draft["fermentables"].items():
        target_weight = (percentage / 100.0) * total_weight
        adjusted_weight_kg = (target_weight / 2.20462)  # Convert to kg
        fermentables[malt] = round(adjusted_weight_kg, 2)

    # 4. Beräkna faktisk OG baserat på justerade vikter
    total_gp = 0.0
    for malt, (_, potential_sg) in draft["fermentables"].items():
        # Ensure potential_sg is valid
        potential_sg = max(1.001, float(potential_sg))
        ppg = (potential_sg - 1) * 1000
        malt_weight_lbs = fermentables[malt] * 2.20462  # Convert kg to lbs
        total_gp += malt_weight_lbs * ppg * efficiency

    # Prevent division by zero in final OG calculation
    post_boil_volume_gallons = max(0.001, post_boil_volume_gallons)
    actual_og = 1 + (total_gp / (post_boil_volume_gallons * 1000))
    
    return {
        "og": round(actual_og, 3),
        "fermentables": fermentables
    }

def calculate_malt_weight(percentage, target_og, post_boil_volume, efficiency, potential_sg):
    """Hjälpfunktion för att beräkna maltvikt"""
    required_points = (target_og - 1) * post_boil_volume
    return (percentage / 100.0) * (required_points / ((potential_sg - 1) * efficiency))

def calculate_ibu(draft: Dict[str, Any], equipment: Dict[str, Any], post_boil_volume: float):
    """
    Calculate IBU contribution from hops using Tinseth formula.
    Added extra debug logging and safeguards for division by zero.
    """
    print("\n=== IBU Calculation Debug ===")
    print(f"Post-boil volume: {post_boil_volume:.2f}L")
    
    # Add safeguard against division by zero
    if post_boil_volume <= 0:
        print("WARNING: Post-boil volume is zero or negative. Using minimum safe value.")
        post_boil_volume = 0.001  # Minimum safe value to avoid division by zero
    
    total_ibu = 0.0
    post_boil_gallons = post_boil_volume * 0.264172  # Liter → gallon
    hops_with_amounts = []
    
    # Debug hop info
    print("DEBUG Hop info:")
    for i, hop in enumerate(draft.get("hops", [])):
        print(f"  - Hop {i+1}: {hop.get('name', 'Unknown')}, Alpha: {hop.get('alpha', 'N/A')}%, Time: {hop.get('time', 'N/A')}min")

    for hop in draft["hops"]:
        # Ensure alpha, time and target_ibu are valid numbers
        alpha = max(0.0001, hop.get("alpha", 0) / 100.0)  # Ensure non-zero
        time = max(0.1, hop.get("time", 0))
        target_ibu = max(0, hop.get("ibu_contribution", 0))
        
        # Print detailed debug info
        print(f"\nCalculating for {hop.get('name', 'Unknown Hop')}:")
        print(f"  Alpha: {alpha:.4f} (decimal), Time: {time} min, Target IBU: {target_ibu}")
        
        # Korrigerad Tinseth utilization formel
        # Bigness factor = 1.65 * 0.000125^(wort gravity - 1)
        bigness_factor = 1.65 * pow(0.000125, 0.050)  # Använder standard 1.050 OG här
        
        # Boil Time factor = (1 - e^(-0.04 * time)) / 4.15
        boil_time_factor = (1 - math.exp(-0.04 * time)) / 4.15
        
        # Total utilization
        utilization = bigness_factor * boil_time_factor
        
        print(f"  Utilization factors - Bigness: {bigness_factor:.4f}, Boil time: {boil_time_factor:.4f}")
        print(f"  Total utilization: {utilization:.4f} ({utilization*100:.1f}%)")
        
        # Prevent division by zero in amount calculation
        if alpha * utilization == 0:
            print("  WARNING: Alpha * utilization is zero! Using minimum value.")
            alpha = max(0.001, alpha)
            utilization = max(0.001, utilization)
        
        # Beräkna mängd humle i ounces (with safeguards against division by zero)
        amount_oz = (target_ibu * post_boil_gallons) / (alpha * 7489.2 * utilization)  # 7489.2 är en konstant för metrisk konvertering
        amount_g = amount_oz * 28.3495  # Omvandla till gram

        print(f"  Calculated amount: {amount_g:.1f}g ({amount_oz:.2f}oz)")

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

    # Ensure we never return NaN or infinity values
    total_ibu = max(0, min(150, total_ibu))  # Cap between 0 and 150 IBUs
    print(f"\nFinal IBU calculation: {total_ibu:.1f}")
    
    return total_ibu, hops_with_amounts


def calculate_ebc(draft: Dict[str, Any], fermentables: Dict[str, float], post_boil_volume: float) -> float:
    """
    Beräknar EBC baserat på maltvikter och färgvärden.
    """
    print("\n=== EBC Calculation Debug ===")
    print(f"Post-boil volume: {post_boil_volume:.2f}L")
    
    # Add safeguard against division by zero
    if post_boil_volume <= 0:
        print("WARNING: Post-boil volume is zero or negative. Using minimum safe value.")
        post_boil_volume = 0.001  # Minimum safe value to avoid division by zero

    post_boil_gallons = post_boil_volume * 0.264172
    total_mcu = 0.0

    print("\nMalt Color Calculations:")
    for malt, weight_kg in fermentables.items():
        # Hämta SRM-värde från Brewfather metadata
        srm_color = draft["fermentables_metadata"][malt].get("color", 0)
        weight_lbs = weight_kg * 2.20462
        
        # Beräkna MCU direkt från SRM (skippar Lovibond-konvertering)
        mcu = (srm_color * weight_lbs) / post_boil_gallons
        total_mcu += mcu

        print(f"\n{malt}:")
        print(f"  Weight: {weight_kg:.2f}kg ({weight_lbs:.2f}lbs)")
        print(f"  Color: {srm_color} SRM")
        print(f"  MCU contribution: {mcu:.1f}")

    # Beräkna SRM och konvertera till EBC
    srm = 1.49 * (total_mcu ** 0.69)
    ebc = srm * 1.97

    print(f"\nFinal Calculations:")
    print(f"Total MCU: {total_mcu:.1f}")
    print(f"Final SRM: {srm:.1f}")
    print(f"Final EBC: {ebc:.1f}")
    
    # Ensure we never return NaN or infinity values
    ebc = max(0, min(80, ebc))  # Cap between 0 and 80 EBC

    return round(ebc, 1)

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
        f'        <EFFICIENCY>{equipment["params"]["brewhouse_efficiency"]}</EFFICIENCY>'
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
    for malt_name, values in draft["fermentables"].items():
        percentage = values[0]  # Använd procentandelen från draft
        malt_metadata = draft["fermentables_metadata"].get(malt_name, {})
        
        xml_parts.extend([
            '            <FERMENTABLE>',
            f'                <NAME>{malt_name}</NAME>',
            f'                <VERSION>1</VERSION>',
            f'                <TYPE>{malt_metadata.get("type", "Grain")}</TYPE>',
            f'                <AMOUNT>{calculated["fermentables"][malt_name]}</AMOUNT>',  # Använd vikten från calculated
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