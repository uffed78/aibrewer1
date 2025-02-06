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
        total_percentage = sum(draft["fermentables"].values())
        if not math.isclose(total_percentage, 100, abs_tol=0.1):  # Tillåter liten avrundningsskillnad
            errors.append(f"Maltfördelningen summerar till {total_percentage}%, måste vara 100%.")
    
    # 2. Validera humle
    if "hops" not in draft:
        errors.append("Ingen humle angiven.")
    else:
        for hop in draft["hops"]:
            if "time" not in hop or "amount" not in hop:
                errors.append("Varje humle måste ha 'time' och 'amount' angivna.")
    
    # 3. Validera jäst
    if "yeast" not in draft:
        errors.append("Ingen jäst angiven.")
    elif "type" not in draft["yeast"] or "amount" not in draft["yeast"]:
        errors.append("Jäst måste ha 'type' och 'amount' angivna.")
    
    return {
        "valid": len(errors) == 0,
        "message": "; ".join(errors) if errors else "Receptutkastet är giltigt."
    }

def calculate_og(draft: Dict[str, Any], equipment: Dict[str, Any]) -> float:
    """
    Beräknar OG (Original Gravity) baserat på maltfördelning och utrustning.
    
    Args:
        draft (Dict): Receptutkastet från GPT.
        equipment (Dict): Utrustningsprofilen.
        
    Returns:
        float: Beräknat OG-värde.
    """
    total_points = 0.0
    efficiency = equipment["params"]["efficiency"] / 100.0  # Konvertera till decimalform
    
    for malt, (percentage, potential_sg) in draft["fermentables"].items():
        malt_points = (potential_sg - 1) * (percentage / 100.0) * efficiency
        total_points += malt_points
    
    batch_size = equipment["params"]["batch_size"]
    return round(1 + (total_points / batch_size), 3)  # Avrunda till 3 decimaler

def calculate_ibu(draft: Dict[str, Any], equipment: Dict[str, Any]) -> float:
    """
    Beräknar IBU (International Bitterness Units) med Tinseth-formeln.
    
    Args:
        draft (Dict): Receptutkastet från GPT.
        equipment (Dict): Utrustningsprofilen.
        
    Returns:
        float: Beräknat IBU-värde.
    """
    total_ibu = 0.0
    batch_size = equipment["params"]["batch_size"]
    
    for hop in draft["hops"]:
        alpha_acid = hop.get("alpha", 0)  # Standardvärde om inte angivet
        amount = hop["amount"]  # i gram
        time = hop["time"]  # i minuter
        
        # Tinseth-formeln
        utilization = (1.65 * 0.000125 ** (batch_size - 1)) * (1 - math.exp(-0.04 * time)) / 4.15
        ibu_contribution = (amount * alpha_acid * utilization) / batch_size
        total_ibu += ibu_contribution
    
    return round(total_ibu, 1)  # Avrunda till 1 decimal

def calculate_ebc(draft: Dict[str, Any], equipment: Dict[str, Any]) -> float:
    """
    Beräknar EBC (European Brewery Convention) för färg.
    
    Args:
        draft (Dict): Receptutkastet från GPT.
        equipment (Dict): Utrustningsprofilen.
        
    Returns:
        float: Beräknat EBC-värde.
    """
    total_mcu = 0.0
    batch_size = equipment["params"]["batch_size"]
    
    for malt, (percentage, color_lovibond) in draft["fermentables"].items():
        mcu = (color_lovibond * (percentage / 100.0)) / batch_size
        total_mcu += mcu
    
    srm = 1.49 * (total_mcu ** 0.69)
    return round(srm * 1.97, 1)  # Konvertera SRM till EBC och avrunda

def generate_beerxml(draft: Dict[str, Any], calculated: Dict[str, Any], equipment: Dict[str, Any]) -> str:
    """
    Genererar en BeerXML-fil baserat på receptutkastet och beräknade värden.
    
    Args:
        draft (Dict): Receptutkastet från GPT.
        calculated (Dict): Beräknade värden (OG, IBU, EBC).
        equipment (Dict): Utrustningsprofilen.
        
    Returns:
        str: En korrekt formaterad BeerXML-sträng.
    """
    return f"""<?xml version="1.0"?>
<RECIPES>
  <RECIPE>
    <NAME>{draft.get("name", "Custom Recipe")}</NAME>
    <BREWER>{equipment.get("brewer", "Unknown Brewer")}</BREWER>
    <BATCH_SIZE>{equipment["params"]["batch_size"]}</BATCH_SIZE>
    <BOIL_SIZE>{equipment["params"]["boil_size"]}</BOIL_SIZE>
    <BOIL_TIME>{equipment["params"]["boil_time"]}</BOIL_TIME>
    <EFFICIENCY>{equipment["params"]["efficiency"]}</EFFICIENCY>
    <OG>{calculated["og"]}</OG>
    <IBU>{calculated["ibu"]}</IBU>
    <COLOR>{calculated["ebc"]}</COLOR>
    <FERMENTABLES>
      {"".join(
          f'<FERMENTABLE><NAME>{malt}</NAME><AMOUNT>{percentage}</AMOUNT></FERMENTABLE>'
          for malt, (percentage, _) in draft["fermentables"].items()
      )}
    </FERMENTABLES>
    <HOPS>
      {"".join(
          f'<HOP><NAME>{hop["name"]}</NAME><AMOUNT>{hop["amount"]}</AMOUNT><TIME>{hop["time"]}</TIME></HOP>'
          for hop in draft["hops"]
      )}
    </HOPS>
    <YEASTS>
      <YEAST>
        <NAME>{draft["yeast"]["type"]}</NAME>
        <AMOUNT>{draft["yeast"]["amount"]}</AMOUNT>
      </YEAST>
    </YEASTS>
  </RECIPE>
</RECIPES>"""
