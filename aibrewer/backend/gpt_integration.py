import openai
import os
from dotenv import load_dotenv

# Ladda miljövariabler från .env
load_dotenv()

# Ställ in OpenAI API-nyckel
openai.api_key = os.getenv("OPENAI_API_KEY")

# OpenAI-klientinstans
client = openai.OpenAI()

# Din assistent-ID
assistant_id = "asst_BEIODxwjFATTFmQFyTBOEBGr"

def generate_recipe_with_gpt(user_prompt):
    """
    Genererar recept via OpenAI-assistenten baserat på användarens prompt.
    """
    try:
        # Skapa en ny tråd
        thread = client.beta.threads.create()
        print(f"Thread created: {thread.id}")  # Debug

        # Lägg till användarens meddelande i tråden
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_prompt
        )
        print(f"User message added to thread: {user_prompt}")  # Debug

        # Kör assistenten
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        print(f"Run status: {run.status}")  # Debug

        # Kontrollera om körningen lyckades
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for message in messages:
                if message.content[0].type == "text":
                    return message.content[0].text.value

        return {"error": "Run did not complete successfully."}

    except Exception as e:
        print(f"Error in generate_recipe_with_gpt: {str(e)}")
        return {"error": str(e)}

def continue_gpt_conversation(messages):
    """
    Fortsätter konversationen med GPT baserat på tidigare meddelanden.
    """
    try:
        # Skapa en ny tråd för konversationen
        thread = client.beta.threads.create()
        print(f"Thread created: {thread.id}")  # Debug

        # Lägg till alla tidigare meddelanden i tråden
        for msg in messages:
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role=msg["role"],
                content=msg["content"]
            )
        print("Messages added to thread.")  # Debug

        # Kör assistenten
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        print(f"Run status: {run.status}")  # Debug

        # Kontrollera om körningen lyckades
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for message in messages:
                if message.content[0].type == "text":
                    return message.content[0].text.value

        return {"error": "Run did not complete successfully."}

    except Exception as e:
        print(f"Error in continue_gpt_conversation: {str(e)}")
        return {"error": str(e)}

def format_recipe_data(recipe_data):
    """
    Formaterar receptdata för att skapa en sammanfattning åt GPT.
    :param recipe_data: Dictionary med receptdata.
    :return: Sträng som innehåller den formaterade receptinformationen.
    """
    try:
        # Grundläggande receptinformation
        name = recipe_data.get("name", "Unknown Name")
        style = recipe_data.get("style", {}).get("name", "Unknown Style")
        abv = recipe_data.get("abv", "Unknown ABV")
        ibu = recipe_data.get("ibu", "Unknown IBU")
        notes = recipe_data.get("notes", "No notes provided.")

        # Ingredienser
        fermentables = recipe_data.get("fermentables", [])
        hops = recipe_data.get("hops", [])
        yeasts = recipe_data.get("yeasts", [])

        # Formaterade listor
        formatted_fermentables = "\n".join(
            [f"- {f.get('name', 'Unknown')} ({f.get('amount', 0)} kg)" for f in fermentables]
        )
        formatted_hops = "\n".join(
            [f"- {h.get('name', 'Unknown')} ({h.get('amount', 0)} g, {h.get('alpha', 0)}% alpha acids)" for h in hops]
        )
        formatted_yeasts = "\n".join(
            [f"- {y.get('name', 'Unknown')} ({y.get('amount', 0)} packs)" for y in yeasts]
        )

        # Skapa sammanfattningen
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
    Skickar hela inventariedatan, inklusive alla attribut, till GPT.
    :param full_inventory: Komplett inventariedata från Brewfather.
    :return: GPT:s svar.
    """
    try:
        # Skapa en ny tråd
        thread = client.beta.threads.create()
        print(f"Thread created: {thread.id}")  # Debug

        # Skicka hela inventariedatan direkt till GPT
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=str(full_inventory)  # Konvertera till sträng för att skicka som text
        )
        print("Full inventory data sent to GPT.")  # Debug

        # Kör assistenten
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        print(f"Run status: {run.status}")  # Debug

        # Kontrollera om körningen lyckades
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for message in messages:
                if "content" in message and "type" in message.content[0] and message.content[0].type == "text":
                    return message.content[0].text.value

        return {"error": "Run did not complete successfully."}

    except Exception as e:
        print(f"Error in send_full_inventory_to_gpt: {str(e)}")
        return {"error": str(e)}

def save_recipe_to_file(filename, content):
    directory = os.path.join(os.getcwd(), 'data')  # Lokal katalog
    if not os.path.exists(directory):
        os.makedirs(directory)  # Skapa katalogen om den inte finns

    file_path = os.path.join(directory, filename)
    with open(file_path, "w") as file:
        file.write(content)
    print(f"File saved at: {file_path}")
    return file_path
