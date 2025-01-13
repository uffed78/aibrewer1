import openai
import os
from dotenv import load_dotenv

# Ladda miljövariabler från .env
load_dotenv()

# Ställ in OpenAI API-nyckel
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_recipe_with_gpt(user_prompt):
    """
    Genererar recept baserat på användarens prompt med OpenAI:s korrekt konfigurerade chat-komplettering.
    :param user_prompt: Sträng med användarens beskrivning/krav.
    :return: GPT-genererad text.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant for creating beer recipes."},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        # Extrahera innehåll från svaret
        choices = response.choices
        if choices and len(choices) > 0:
            return choices[0].message.content
        else:
            return "No content returned from OpenAI."
    except Exception as e:
        return {"error": str(e)}

def continue_gpt_conversation(messages):
    """
    Fortsätter konversationen med GPT baserat på givna meddelanden.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        print("GPT Response Object:", response)  # Debugutskrift
        return response
    except Exception as e:
        print("Fel i continue_gpt_conversation:", str(e))
        return {"error": str(e)}

def format_recipe_data(recipe_data):
    """
    Förbättrad funktion för att extrahera och formatera relevant receptdata.
    """
    try:
        # Grundläggande information
        name = recipe_data.get("name", "Okänt namn")
        abv = recipe_data.get("abv", "Okänd ABV")
        ibu = recipe_data.get("ibu", "Okänd IBU")
        style = recipe_data.get("style", {}).get("name", "Okänd stil")
        notes = recipe_data.get("notes", "Inga anteckningar")
        
        # Extrahera fermentables (malt)
        fermentables = recipe_data.get("fermentables", [])
        malt_list = [
            f"{malt.get('name', 'Okänd malt')} ({malt.get('amount', 0)} kg, {malt.get('percentage', 0)}%)"
            for malt in fermentables
        ]

        # Extrahera humle
        hops = recipe_data.get("hops", [])
        hops_list = [
            f"{hop.get('name', 'Okänd humle')} ({hop.get('amount', 0)} g, {hop.get('alpha', 0)}% alfa)"
            for hop in hops
        ]

        # Extrahera jäst
        yeasts = recipe_data.get("yeasts", [])
        yeast_list = [
            f"{yeast.get('name', 'Okänd jäst')} ({yeast.get('amount', 0)} paket)"
            for yeast in yeasts
        ]

        # Bygg en sammanfattad text för GPT
        formatted_data = f"""
        Receptnamn: {name}
        Stil: {style}
        ABV: {abv}%
        IBU: {ibu}

        Ingredienser:
        Malt:
        - {"\n        - ".join(malt_list)}
        Humle:
        - {"\n        - ".join(hops_list)}
        Jäst:
        - {"\n        - ".join(yeast_list)}

        Anteckningar:
        {notes}
        """
        return formatted_data.strip()
    except Exception as e:
        return f"Fel vid formatering av data: {str(e)}"


