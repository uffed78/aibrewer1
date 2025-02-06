def calculate_recipe_values(recipe_draft, profile_name):
    try:
        # Hämta bryggverksprofil
        profile = get_equipment_profile(profile_name)
        if not profile:
            return {"error": "Invalid brewing profile"}

        # Beräkna OG, FG, ABV, IBU, EBC
        batch_size = 23  # Standard batchstorlek
        efficiency = 75  # Standard effektivitet
        og = 1.045  # Placeholder
        fg = 1.010  # Placeholder
        abv = round((og - fg) * 131.25, 2)
        ibu = 30  # Placeholder
        ebc = 10  # Placeholder

        # Returnera beräknade värden
        return {
            "OG": round(og, 3),
            "FG": round(fg, 3),
            "ABV": abv,
            "IBU": ibu,
            "EBC": ebc,
            "profile": profile["xml"]
        }

    except Exception as e:
        return {"error": str(e)}
