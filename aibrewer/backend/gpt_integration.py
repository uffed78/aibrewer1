import os
from dotenv import load_dotenv
from openai import OpenAI

# Ladda miljövariabler från .env
load_dotenv()

# Ställ in OpenRouter API-konfiguration
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def generate_recipe_with_gpt(user_prompt):
    """
    Genererar ett ölrecept baserat på användarens prompt med OpenRouter.
    """
    try:
        if not user_prompt or user_prompt.strip() == "":
            print("DEBUG: user_prompt är tomt! Avbryter anrop till OpenRouter.")
            return {"error": "User prompt is empty"}

        print("DEBUG: Skickar följande prompt till GPT:")
        print(user_prompt)

        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",
                "X-Title": "<YOUR_SITE_NAME>",
            },
            model="anthropic/claude-3.5-haiku-20241022:beta",
            messages=[
                {"role": "system", "content": "Du är en expert på ölbryggning och receptutveckling."},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=5000,
            temperature=0.7
        )

        print("DEBUG: OpenRouter Response:", response)

        choices = response.choices
        if choices and len(choices) > 0:
            return choices[0].message.content.strip()
        else:
            return {"error": "No content returned from GPT."}

    except Exception as e:
        print(f"Error in generate_recipe_with_gpt: {str(e)}")
        return {"error": str(e)}



def continue_gpt_conversation(messages):
    """
    Fortsätter konversationen med GPT via OpenRouter och ser till att kontexten bevaras.
    """
    try:
        if not messages:
            return "Jag har ingen tidigare kontext att fortsätta ifrån."

        # Lägg till en system-prompt för att ge GPT rätt kontext
        system_prompt = {
            "role": "system",
            "content": "Du är en öl-expert och bryggmästare. Användaren har delat sitt inventory, valt en ölstil och fått ett receptförslag. \
                        Fortsätt samtalet baserat på tidigare meddelanden och hjälp användaren att förbättra receptet."
        }

        # Se till att systemmeddelandet är med i varje anrop
        if not any(msg["role"] == "system" for msg in messages):
            messages.insert(0, system_prompt)

        print("📡 Meddelanden som skickas till GPT:", messages)

        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",
                "X-Title": "<YOUR_SITE_NAME>",
            },
            model="anthropic/claude-3.5-haiku-20241022:beta",
            messages=messages,
            max_tokens=5000,
            temperature=0.7
        )

        print("📡 GPT Raw Response:", response)

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Fel i continue_gpt_conversation: {str(e)}")
        return {"error": str(e)}

def send_full_inventory_to_gpt(full_inventory):
    """
    Skickar hela inventariedatan till GPT via OpenRouter.
    """
    try:
        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",
                "X-Title": "<YOUR_SITE_NAME>",
            },
            model="anthropic/claude-3.5-haiku-20241022:beta",
            messages=[
                {"role": "system", "content": "Du är en expert på ölbryggning och BeerXML-recept."},
                {"role": "user", "content": str(full_inventory)}
            ],
            max_tokens=5000,
            temperature=0.7
        )

        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            return {"error": "No valid response from GPT."}
    except Exception as e:
        print(f"Error in send_full_inventory_to_gpt: {str(e)}")
        return {"error": str(e)}