# Uppdateringar för Render-deployment

## Problemet

Bygget på Render misslyckas när det försöker installera `gevent==21.12.0` eftersom:

1. Denna version är inte kompatibel med Python 3.11 (som används på Render)
2. Cython-koden i gevent försöker använda `long`-typen som bara finns i Python 2

## Lösningen

1. Ta bort gevent-beroendet från requirements.txt
2. Använda gunicorn med standardinställningen `sync` worker istället för `gevent`

## Ytterligare åtgärder om detta inte räcker

Om din app verkligen behöver async-stöd, kan du prova något av dessa alternativ:

1. Uppdatera till en nyare gevent-version som är kompatibel med Python 3.11:
   ```
   gevent>=22.10.2
   ```

2. Använd alternativen `eventlet` eller `uvicorn` som worker-klass:
   ```
   pip install eventlet
   ```
   och i gunicorn_config.py:
   ```python
   worker_class = 'eventlet'
   ```

3. Ange en specifik Python-version för Render-miljön (t.ex. 3.9) genom att skapa en `.python-version` fil:
   ```
   echo "3.9.13" > .python-version
   ```
