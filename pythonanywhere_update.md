# Uppdatera AIBrewer på PythonAnywhere

## 1. Logga in på PythonAnywhere

Gå till [PythonAnywhere.com](https://www.pythonanywhere.com/) och logga in på ditt konto.

## 2. Öppna en Bash-konsol

- Klicka på "Consoles" i den övre menyn
- Välj "Bash" för att öppna en ny terminal

## 3. Navigera till ditt projekt och uppdatera koden

```bash
# Gå till din projektmapp
cd aibrewer1

# Se till att du är på rätt branch
git branch

# Om du behöver byta branch
git checkout Backend_calculations

# Uppdatera koden genom att hämta senaste ändringarna
git pull origin Backend_calculations

# Kontrollera att uppdateringen lyckades
ls -la
git status
```

## 4. Uppdatera eventuella nya beroenden

Om du har lagt till nya paket i requirements.txt:

```bash
# Aktivera din virtuella miljö
workon aibrewer-env

# Installera nya beroenden
pip install -r requirements.txt
```

## 5. Starta om webbappen

- Gå till "Web" i den övre menyn
- Klicka på den gröna "Reload" knappen för din webapp

## 6. Kontrollera loggarna för fel

Om något går fel efter omstarten:

- Kolla "Error log" under "Web" → "Logs"-sektionen
- Vanliga fel kan vara saknade beroenden eller konfigurationsfel

## 7. Rensa webbläsarens cache

För att se till att du ser den senaste versionen av din app, rensa webbläsarens cache eller använd ett inkognitofönster för att besöka din app.

---

## Lösa vanliga problem

### Problem med Git Pull

Om `git pull` misslyckas på grund av lokala ändringar:

```bash
# Se vilka filer som ändrats lokalt
git status

# Om du inte bryr dig om lokala ändringar, återställ dem
git reset --hard HEAD
git pull origin Backend_calculations
```

### Problem med moduler som inte hittas

Om du får ImportError efter uppdateringen:

1. Kontrollera att WSGI-filen pekar på rätt katalog
2. Säkerställ att alla nya moduler är installerade
3. Kontrollera att relativa importer är korrekta
