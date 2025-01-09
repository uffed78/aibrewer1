import requests
import os
import base64
from dotenv import load_dotenv

# Ladda miljövariabler från .env
load_dotenv()

# Brewfather API-autentisering
BREWFATHER_USERID = os.getenv("BREWFATHER_USERID")
BREWFATHER_APIKEY = os.getenv("BREWFATHER_APIKEY")
BASE_URL = "https://api.brewfather.app/v2"

def get_inventory(category):
    """
    Hämtar inventariedata från Brewfather API.
    :param category: fermentables, hops, yeasts, miscs
    :return: JSON-data eller felmeddelande
    """
    try:
        url = f"{BASE_URL}/inventory/{category}"
        credentials = f"{BREWFATHER_USERID}:{BREWFATHER_APIKEY}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch {category}. Status code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_recipes():
    """
    Hämtar recept från Brewfather API.
    :return: JSON-data eller felmeddelande
    """
    try:
        url = f"{BASE_URL}/recipes"
        credentials = f"{BREWFATHER_USERID}:{BREWFATHER_APIKEY}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch recipes. Status code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
