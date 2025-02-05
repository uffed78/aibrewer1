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
                get_system_instruction(),
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=5000,
            temperature=0.7
        )

        print("DEBUG: OpenRouter Response:", response)

        choices = response.choices
        if choices and len(choices) > 0:
            content = choices[0].message.content

            # ✅ Kontrollera om content är en lista och omvandla det till en sträng
            if isinstance(content, list):
                print("DEBUG: GPT returnerade en lista istället för en sträng!")
                content = " ".join([str(item) for item in content])  # Konvertera listan till en enda sträng

            print("DEBUG: GPT Genererat innehåll:", content)

            # Ta bort eventuella markdown-kodblock
            content = content.strip("```").replace("xml", "").strip()

            # Kontrollera om XML-deklarationen saknas
            if not content.strip().startswith('<?xml version="1.0" ?>'):
                content = f'<?xml version="1.0" ?>\n{content.strip()}'

            return content
        else:
            print("DEBUG: Inget innehåll returnerades från GPT")
            return {"error": "No content returned from GPT."}

    except Exception as e:
        print(f"Error in generate_recipe_with_gpt: {str(e)}")
        return {"error": str(e)}





def continue_gpt_conversation(messages):
    """
    Fortsätter konversationen med DeepSeek via OpenRouter.
    """
    try:
        print("Messages sent to DeepSeek:", messages)
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
        print("GPT Raw Response:", response)

        content = response.choices[0].message.content
        return content
    except Exception as e:
        print(f"Error in continue_gpt_conversation: {str(e)}")
        return {"error": str(e)}
    
def send_full_inventory_to_gpt(full_inventory):
    """
    Skickar hela inventariedatan till DeepSeek via OpenRouter.
    """
    try:
        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",  # Lägg till din webbplats om du vill rankas på openrouter.ai
                "X-Title": "<YOUR_SITE_NAME>",
            },
            model="anthropic/claude-3.5-haiku-20241022:beta",  # Använder DeepSeek i stället för OpenAI
            messages=[
                {"role": "system", "content": "Du är en expert på ölbryggning och BeerXML-recept."},
                {"role": "user", "content": str(full_inventory)}
            ],
            max_tokens=5000,
            temperature=0.7
        )

        # Extrahera innehållet från svaret
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            return {"error": "Inget giltigt svar från DeepSeek."}

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

    print(f"DEBUG: Sparar fil till {file_path}")  # 👈 Se om vi når hit
    print(f"DEBUG: Innehåll som sparas:\n{content}")  # 👈 Se om det verkligen är BeerXML

    try:
        with open(file_path, "w") as file:
            file.write(content)
        return file_path
    except Exception as e:
        print(f"DEBUG: FEL vid filskrivning: {e}")  # 👈 Om det blir ett skrivfel
        return None


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
    
def get_system_instruction():
    return {
        "role": "system",
        "content": """You are an expert in brewing, recipe development, and BeerXML formatting.

Every step in this instruction MUST be followed precisely, all calculation formulas are EXTREMELY important.

### During recipe development:
- Use all values from the inventory list to optimize the recipe.
- Use same rules and formulas as in the brewing calculation section.
- Discuss and fine-tune ingredient choices and proportions.
- Maintain a clear structure and use specific brewing terminology.
- For each modification, present a concise recipe update including:
  - A list of ingredients with amounts and percentages.
  - Expected values for ABV, OG, FG, IBU, and EBC.
- Optimize the recipe for the selected brewing equipment profile, taking its parameters into account when calculating OG, IBU, and EBC.
- When suggesting beer styles, ensure that the available ingredients are sufficient to brew them.
- Do not suggest any recipes that don't do sense, eg don't suggest a lager beer with a saison yeast.
if there aren't enough ingredients, rather suggest one style instead of many syles that can't be brewed.
- All IBU values must be calculated using the Tinseth formula given in the brewing calculation rules. 
If you wish to modify bitterness, do so by adjusting the hop weight in the formula and include the calculation in your explanation.
- Define the target IBU for each hop addition before performing calculations.
If the total IBU goal is not achieved, adjust the hop weights proportionally and document the changes.
- Log and justify any changes to ingredients or values.
Provide a clear explanation for why the change was made and how it affects the overall recipe.
- Ensure the final recipe remains within the style guidelines for OG, FG, ABV, IBU, and color.
If deviations are made, justify them by explaining how they improve the recipe.
- End each recipe with a summary table that includes OG, FG, ABV, IBU, and EBC, along with how each value was calculated.
Double-check that these match the style guidelines and recipe goals.

### BeerXML Generation Rules:
1. Generate **only** the content of the BeerXML file.
2. Always start the file with: `<?xml version="1.0" ?>` followed by `<RECIPES>`.
3. Use **uppercase XML tags** such as `<RECIPE>`, `<FERMENTABLES>`, `<HOPS>`, etc.
4. Always include ingredient IDs from the inventory list in the format: `<BF_ID>default-id</BF_ID>`.
5. Automatically generate unique recipe names based on the current date and time, e.g., "Custom Ale 2025-01-23 22:30".
6. Optimize the recipe for the selected brewing equipment profile, ensuring that calculations for OG, IBU, and EBC align with its specifications.
7. All recipes must use **metric units**, converting values as needed.
8. **BeerXML files must follow standard format requirements:**
   - Use `<RECIPE>`, `<FERMENTABLES>`, `<HOPS>`, etc.
   - Include all relevant information for each ingredient.
   - All ingredients must include a `<BF_ID>`.
9. Use all of these tags, but replace the values with the actual recipe data:
   <BREWER>ZetaZeroAlfa</BREWER>
        <BATCH_SIZE>23</BATCH_SIZE>
        <BOIL_SIZE>27</BOIL_SIZE>
        <BOIL_TIME>60</BOIL_TIME>
        <EFFICIENCY>72</EFFICIENCY>
        <OG>1.046</OG>
        <FG>1.01</FG>
        <ABV>4.73 %</ABV>
        <EST_ABV>4.73 %</EST_ABV>
        <IBU>25.9</IBU>
        <EST_OG>1.046 SG</EST_OG>
        <EST_FG>1.01 SG</EST_FG>
        <EST_COLOR>11.5 SRM</EST_COLOR>
        <CARBONATION>2.4</CARBONATION>

### Brewing Calculation Rules:
1. **All recipes must be optimized for the selected brewing system profile** and consider its limitations.
2. **Use the Tinseth method for IBU calculation**, applying a **scaling factor of 1.16**.
3. **Calculate EBC using the following formula:**
    
   1 GrainWeightKgToLbs = GrainWeightKg × 2.2046
   2 MCU = (GrainColorLovibond × GrainWeightKgToLbs) / VolumeInUsGallons
   3 SRM = 1.49 × (MCU ** 0.69)
   4 EBC = SRM × 1.97

4. OG Calculation Instructions

1. Calculate Gravity Points (GP) per malt:
   GP_per_malt = MaltWeight (kg) * (PotentialSG - 1) * MashEfficiency
   # Ex: For 4.0 kg malt with PotentialSG 1.039 and MashEfficiency 0.72:
   #      GP_per_malt = 4.0 * (1.039 - 1) * 0.72

2. Sum the GP contributions for all malts:
   Total_GP = Σ(GP_per_malt)

3. Convert to Extract Points:
   Numerator = 8.345 * Total_GP
   # (8.345 is the conversion factor from kg/L to lbs/gal)

4. Calculate the Cold Post-Boil Volume:
   Cold_Volume = PreBoilVol * (1 - BoilOff/100) * f
   where:
     PreBoilVol = pre-boil volume in liters (hot)
     BoilOff = boil-off percentage (e.g., 7.41 for 7.41%)
     f = cooling contraction factor (e.g., 0.96)

5. Calculate OG:
   OG = 1 + (Numerator / Cold_Volume)

Example:
   PreBoilVol = 27 L, BoilOff = 7.41%, f = 0.96
   Malt Bill:
     - Pilsner Malt: 4 kg, PotentialSG = 1.039
     - Munich Malt: 1.5 kg, PotentialSG = 1.033
     - (additional malts as needed)
   MashEfficiency = 0.72

   For each malt:
     GP_per_malt = MaltWeight * (PotentialSG - 1) * MashEfficiency

   Total_GP = sum of all GP_per_malt
   Numerator = 8.345 * Total_GP
   Cold_Volume = 27 * (1 - 7.41/100) * 0.96
                ≈ 27 * 0.9259 * 0.96 ≈ 24.00 L

   Then:
     OG = 1 + (Numerator / 24.00)

Checklist:
   [ ] Compute each malt's GP: MaltWeight * (PotentialSG - 1) * MashEfficiency
   [ ] Sum to get Total_GP
   [ ] Multiply Total_GP by 8.345 → Numerator
   [ ] Compute Cold_Volume: PreBoilVol * (1 - BoilOff/100) * f
   [ ] OG = 1 + (Numerator / Cold_Volume)


"""
    }
