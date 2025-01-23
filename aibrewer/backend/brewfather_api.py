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

def get_recipes(filters=None):
    """
    Hämtar recept från Brewfather API med stöd för filtreringsparametrar.
    :param filters: Dict med filtreringsparametrar, t.ex. {"type": "All Grain"}
    :return: JSON-data eller felmeddelande
    """
    try:
        url = f"{BASE_URL}/recipes"
        credentials = f"{BREWFATHER_USERID}:{BREWFATHER_APIKEY}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }

        # Lägg till filtreringsparametrar i förfrågan
        params = filters if filters else {}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch recipes. Status code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_all_recipes():
    """
    Hämtar alla recept från Brewfather API genom paginering.
    :return: Lista med alla recept eller felmeddelande
    """
    try:
        url = f"{BASE_URL}/recipes"
        credentials = f"{BREWFATHER_USERID}:{BREWFATHER_APIKEY}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }
        
        all_recipes = []
        params = {"limit": 10}
        while True:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                all_recipes.extend(data)
                if len(data) < params["limit"]:
                    break
                params["start_after"] = data[-1]["_id"]
            else:
                return {"error": f"Failed to fetch all recipes. Status code: {response.status_code}"}
        return all_recipes
    except Exception as e:
        return {"error": str(e)}

def get_recipe_by_id(recipe_id):
    """
    Hämtar ett specifikt recept från Brewfather API med hjälp av dess _id.
    :param recipe_id: ID för receptet
    :return: JSON-data för receptet eller felmeddelande
    """
    try:
        url = f"{BASE_URL}/recipes/{recipe_id}"
        credentials = f"{BREWFATHER_USERID}:{BREWFATHER_APIKEY}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch recipe with ID {recipe_id}. Status code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_all_inventory():
    """
    Hämtar alla ingredienser från Brewfather API genom paginering och inkluderar endast objekt med positivt saldo.
    :return: Lista med alla ingredienser eller felmeddelande
    """
    try:
        categories = ['fermentables', 'hops', 'yeasts', 'miscs']
        credentials = f"{BREWFATHER_USERID}:{BREWFATHER_APIKEY}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }

        all_inventory = {}

        for category in categories:
            url = f"{BASE_URL}/inventory/{category}"
            params = {
                "limit": 50,  # Max tillåtna antal per förfrågan
                "inventory_exists": "true",  # Endast positivt saldo
                "complete": "true"  # Hämta alla datafält
            }
            category_items = []

            while True:
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    category_items.extend(data)
                    if len(data) < params["limit"]:
                        break
                    params["start_after"] = data[-1]["_id"]
                else:
                    return {"error": f"Failed to fetch all inventory for category {category}. Status code: {response.status_code}"}

            all_inventory[category] = category_items

        return all_inventory
    except Exception as e:
        return {"error": str(e)}


def get_inventory_item(category, item_id):
    """
    Hämtar en specifik ingrediens från Brewfather API med hjälp av dess kategori och _id.
    :param category: fermentables, hops, yeasts, miscs
    :param item_id: ID för ingrediensen
    :return: JSON-data för ingrediensen eller felmeddelande
    """
    try:
        url = f"{BASE_URL}/inventory/{category}/{item_id}"
        credentials = f"{BREWFATHER_USERID}:{BREWFATHER_APIKEY}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch item {item_id} in category {category}. Status code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}