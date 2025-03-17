import os
import json
from os import environ
from dotenv import load_dotenv
from .brewer_personalities import get_personality  # Use relative import

# Ladda miljövariabler från .env
load_dotenv()

# Ändrad OpenAI klientinitialisering för bättre kompatibilitet
try:
    # Försök först med nyare API-stil
    from openai import OpenAI
    
    # Skapa klienten utan 'proxies' argument som kan orsaka fel på vissa plattformar
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    USING_NEW_API = True
except (ImportError, TypeError):
    try:
        # Fallback till äldre OpenAI API stil
        import openai
        openai.api_base = "https://openrouter.ai/api/v1"
        openai.api_key = os.getenv("OPENROUTER_API_KEY")
        USING_NEW_API = False
        print("Using legacy OpenAI API style")
    except ImportError:
        # Om inget fungerar, visa ett tydligt felmeddelande
        print("ERROR: Could not initialize OpenAI client. Please install openai package with: pip install openai>=1.0.0")
        raise

def generate_recipe_with_gpt(prompt, personality_id="traditionalist"):
    """
    Generates a beer recipe using OpenRouter API based on the provided prompt.
    Compatible with both new and old OpenAI API styles.
    """
    try:
        # Get personality profile if provided
        personality = get_personality(personality_id)
        system_content = personality["system_prompt"] if personality else "You are a master brewer with extensive experience creating high-quality beer recipes."
        
        # Anpassad för olika API-versioner
        if USING_NEW_API:
            # Använd ny API-stil
            response = client.chat.completions.create(
                model="anthropic/claude-3.5-haiku:beta",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            recipe_text = response.choices[0].message.content
        else:
            # Använd äldre API-stil
            response = openai.ChatCompletion.create(
                model="anthropic/claude-3.5-haiku:beta",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            recipe_text = response['choices'][0]['message']['content']
        
        # Try to parse as JSON if possible
        try:
            return json.loads(recipe_text)
        except:
            # Return as plain text if not valid JSON
            return recipe_text
            
    except Exception as e:
        print(f"Error generating recipe with GPT: {str(e)}")
        return {"error": str(e)}

def continue_gpt_conversation(messages, personality_id="traditionalist"):
    """
    Continue a conversation with GPT based on previous messages.
    Compatible with both new and old OpenAI API styles.
    """
    try:
        # Get personality with debug info
        personality = get_personality(personality_id)
        print(f"DEBUG: Using personality {personality_id}: {personality['name']}")
        system_prompt = personality["system_prompt"]
        
        # Create a fresh message array starting with the personality
        full_messages = [{"role": "system", "content": system_prompt}]
        
        # Then add user messages
        full_messages.extend(messages)
        
        print(f"DEBUG: First system message: {full_messages[0]['content'][:50]}...")
        
        # Anpassad för olika API-versioner
        if USING_NEW_API:
            # Använd ny API-stil
            response = client.chat.completions.create(
                model="anthropic/claude-3.5-haiku:beta",
                messages=full_messages,
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content
        else:
            # Använd äldre API-stil
            response = openai.ChatCompletion.create(
                model="anthropic/claude-3.5-haiku:beta",
                messages=full_messages,
                temperature=0.7,
                max_tokens=1500
            )
            return response['choices'][0]['message']['content']
            
    except Exception as e:
        print(f"Error continuing conversation with GPT: {str(e)}")
        return f"Ett fel uppstod när jag försökte generera ett svar: {str(e)}"

def send_full_inventory_to_gpt(full_inventory):
    """
    Skickar hela inventariedatan till GPT.
    """
    try:
        response = client.chat.completions.create(
            model="anthropic/claude-3.5-haiku:beta",  # Use OpenRouter's routing to OpenAI models
            messages=[
                {"role": "system", "content": "Du är en expert på ölbryggning och BeerXML-recept."},
                {"role": "user", "content": str(full_inventory)}
            ],
            max_tokens=1500,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in send_full_inventory_to_gpt: {str(e)}")
        return {"error": str(e)}