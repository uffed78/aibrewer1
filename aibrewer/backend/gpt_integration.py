import os
import json
import openai  # Use the older style import instead of "from openai import OpenAI"
from os import environ
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set API keys from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_recipe_with_gpt(prompt):
    """
    Generates a beer recipe using OpenAI GPT API based on the provided prompt.
    
    Args:
        prompt (str): The prompt to send to GPT for recipe generation.
        
    Returns:
        str: The generated recipe as a string.
    """
    try:
        # Use the older API style
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a master brewer with extensive experience creating high-quality beer recipes."},
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

def continue_gpt_conversation(messages):
    """
    Continue a conversation with GPT based on previous messages.
    
    Args:
        messages (list): A list of message objects in the format 
                        [{"role": "user", "content": "Hello"}, ...]
                        
    Returns:
        str: The response from GPT.
    """
    try:
        # Use the older API style
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        # Extract the content from the response
        return response.choices[0].message.content
            
    except Exception as e:
        print(f"Error continuing conversation with GPT: {str(e)}")
        return {"error": str(e)}

def send_full_inventory_to_gpt(full_inventory):
    """
    Skickar hela inventariedatan till GPT via OpenRouter.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Du är en expert på ölbryggning och BeerXML-recept."},
                {"role": "user", "content": str(full_inventory)}
            ],
            max_tokens=1500,
            temperature=0.7
        )

        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            return {"error": "No valid response from GPT."}
    except Exception as e:
        print(f"Error in send_full_inventory_to_gpt: {str(e)}")
        return {"error": str(e)}