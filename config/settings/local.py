from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Простая локальная БД
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# В локале удобно видеть схему прямо в Swagger
SPECTACULAR_SETTINGS["SERVE_INCLUDE_SCHEMA"] = True

# Почта в консоль
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Повыше уровень логов
LOGGING["root"]["level"] = "DEBUG"

# (Опционально) Django Debug Toolbar
try:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]
except Exception:
    pass
