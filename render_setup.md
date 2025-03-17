# AIBrewer på Render.com

## Steg 1: Registrera dig på Render

1. Gå till [Render.com](https://render.com/) och skapa ett konto
2. Välj "New +" → "Web Service"

## Steg 2: Koppla ditt GitHub-konto

1. I Render Dashboard, välj "Connect account" för GitHub
2. Auktorisera Render att komma åt dina repos
3. Välj ditt `aibrewer1` repository

## Steg 3: Konfigurera tjänsten

1. Ge tjänsten ett namn (t.ex. "aibrewer")
2. Välj branch för deploy (t.ex. "Backend_calculations")
3. Välj Runtime: "Python"
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn aibrewer.backend.app:app`
6. Välj gratis-planen: "Free"

## Steg 4: Lägg till miljövariabler

Under "Environment" sektionen, lägg till:

1. `OPENROUTER_API_KEY`: Din API-nyckel för OpenRouter
2. `PYTHONPATH`: `.` (en punkt för att sätta root-katalogen i Python path)

## Steg 5: Deploy!

1. Klicka på "Create Web Service"
2. Vänta medan Render bygger och startar din app
3. När statusen visar "Live", klicka på URL:en för att besöka din app

## Steg 6: Felsökning

Om något inte fungerar:
1. Kolla loggarna genom att klicka på "Logs" i Render dashboard
2. Kontrollera att alla miljövariabler är korrekt inställda
3. Säkerställ att du har `gunicorn` i `requirements.txt`
4. Verifiera att Flask-appen lyssnar på rätt port (PORT miljövariabeln)

## Steg 7: Hantera utgående HTTP-anslutningar

Till skillnad från PythonAnywhere behöver du inte whitelist-a domäner på Render. 
Alla utgående anrop (t.ex. till Brewfather och OpenRouter) bör fungera direkt utan 
ytterligare konfiguration.
