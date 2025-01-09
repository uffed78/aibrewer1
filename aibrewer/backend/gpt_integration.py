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
