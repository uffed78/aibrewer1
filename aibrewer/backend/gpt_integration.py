import os
import json
from openai import OpenAI
from os import environ
from dotenv import load_dotenv
from .brewer_personalities import get_personality  # Use relative import

# Ladda miljövariabler från .env
load_dotenv()

# Initialize the OpenAI client with OpenRouter configuration
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def generate_recipe_with_gpt(prompt, personality_id="traditionalist"):
    """
    Generates a beer recipe using OpenRouter API based on the provided prompt.
    
    Args:
        prompt (str): The prompt to send to GPT for recipe generation.
        personality_id (str): Optional personality to use for the generation.
        
    Returns:
        str: The generated recipe as a string or JSON object.
    """
    try:
        # Get personality profile if provided
        personality = get_personality(personality_id)
        system_content = personality["system_prompt"] if personality else "You are a master brewer with extensive experience creating high-quality beer recipes."
        
        # Use the client-based API approach with OpenRouter
        response = client.chat.completions.create(
            model="anthropic/claude-3.5-haiku:beta",  # Use OpenRouter's routing to OpenAI models
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Extract the content from the response
        recipe_text = response.choices[0].message.content
        
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
        
        # Make the API call through OpenRouter
        response = client.chat.completions.create(
            model="anthropic/claude-3.5-haiku:beta",
            messages=full_messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
            
    except Exception as e:
        print(f"Error continuing conversation with GPT: {str(e)}")
        return {"error": str(e)}

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