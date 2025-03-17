import os

# Gunicorn konfiguration för produktionsserver
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = 2  # Starter med 2 workers för bättre prestanda
timeout = 120  # Längre timeout för API-anrop
max_requests = 1000
max_requests_jitter = 50
# Ändrad worker_class från 'gevent' till 'sync' (default)
