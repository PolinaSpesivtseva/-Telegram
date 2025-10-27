# example/wsgi.py
import os, sys
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

def log(msg):
    sys.stdout.write(f"[WSGI] {msg}\n"); sys.stdout.flush()

log(f"DJANGO_SETTINGS_MODULE={os.environ['DJANGO_SETTINGS_MODULE']}")
log("…берём приложение Django…")
application = get_wsgi_application()

log("…подключаем WhiteNoise…")
log(f"STATIC_ROOT={settings.STATIC_ROOT!r}, STATIC_URL={settings.STATIC_URL!r}")
application = WhiteNoise(
    application,
    root=settings.STATIC_ROOT,
    prefix=settings.STATIC_URL,
    autorefresh=True,
)
