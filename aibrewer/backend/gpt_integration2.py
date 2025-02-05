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
            max_tokens=5000,  # Begränsar antalet tokens i svaret
            temperature=0.7  # Styr kreativitet
        )

        # Extrahera innehåll från svaret
        choices = response.choices
        if choices and len(choices) > 0:
            content = choices[0].message.content

            # Ta bort eventuella markdown-kodblock
            if content.startswith("```") and content.endswith("```"):
                content = content.strip("```").strip("xml").strip()

            # Kontrollera om XML-deklarationen saknas
            if not content.strip().startswith('<?xml version="1.0" ?>'):
                content = f'<?xml version="1.0" ?>\n{content.strip()}'

            return content
        else:
            return "No content returned from OpenAI."

    except Exception as e:
        return {"error": str(e)}






def continue_gpt_conversation(messages):
    try:
        print("Messages sent to GPT:", messages)
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=5000,
            temperature=0.7
        )
        print("GPT Raw Response:", response)

        # Använd attribut istället för nycklar
        content = response.choices[0].message.content
        return content
    except Exception as e:
        print(f"Error in continue_gpt_conversation: {str(e)}")
        return {"error": str(e)}



def format_recipe_data(recipe_data):
    """
    Formaterar receptdata för att skapa en sammanfattning.
    """
    try:
        name = recipe_data.get("name", "Unknown Name")
        style = recipe_data.get("style", {}).get("name", "Unknown Style")
        abv = recipe_data.get("abv", "Unknown ABV")
        ibu = recipe_data.get("ibu", "Unknown IBU")
        notes = recipe_data.get("notes", "No notes provided.")

        fermentables = recipe_data.get("fermentables", [])
        hops = recipe_data.get("hops", [])
        yeasts = recipe_data.get("yeasts", [])

        formatted_fermentables = "\n".join(
            [f"- {f.get('name', 'Unknown')} ({f.get('amount', 0)} kg)" for f in fermentables]
        )
        formatted_hops = "\n".join(
            [f"- {h.get('name', 'Unknown')} ({h.get('amount', 0)} g, {h.get('alpha', 0)}% alpha acids)" for h in hops]
        )
        formatted_yeasts = "\n".join(
            [f"- {y.get('name', 'Unknown')} ({y.get('amount', 0)} packs)" for y in yeasts]
        )

        return f"""
        Recipe Name: {name}
        Style: {style}
        ABV: {abv}
        IBU: {ibu}

        Ingredients:
        Fermentables:
        {formatted_fermentables}

        Hops:
        {formatted_hops}

        Yeasts:
        {formatted_yeasts}

        Notes:
        {notes}
        """.strip()
    except Exception as e:
        return f"Error formatting recipe data: {str(e)}"

def send_full_inventory_to_gpt(full_inventory):
    """
    Skickar hela inventariedatan till GPT.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du är en expert på ölbryggning och BeerXML-recept."},
                {"role": "user", "content": str(full_inventory)}
            ]
        )

        if response and "choices" in response:
            return response["choices"][0]["message"]["content"]
        else:
            return {"error": "Inget giltigt svar från GPT."}

    except Exception as e:
        print(f"Error in send_full_inventory_to_gpt: {str(e)}")
        return {"error": str(e)}

def save_recipe_to_file(filename, content):
    """
    Sparar receptet i en fil.
    """
    directory = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, filename)
    with open(file_path, "w") as file:
        file.write(content)
    print(f"File saved at: {file_path}")
    return file_path

