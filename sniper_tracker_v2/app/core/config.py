import os

# Единое место для настроек из окружения (.env)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# Ключ подписи JWT. Без надёжного ключа любой может подделать токен и войти в чужой аккаунт,
# поэтому сервер отказывается стартовать с пустым, коротким или шаблонным ключом.
_PLACEHOLDER_SECRETS = {"", "your_secret_key_here", "fallback-secret-key", "changeme", "secret"}
SECRET_KEY = os.getenv("SECRET_KEY", "").strip().strip('"').strip("'")
if SECRET_KEY in _PLACEHOLDER_SECRETS or len(SECRET_KEY) < 32:
    raise RuntimeError(
        "SECRET_KEY не задан или небезопасен. Сгенерируйте ключ: "
        "python -c \"import secrets; print(secrets.token_urlsafe(64))\" и пропишите его в .env"
    )

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Адреса фронтенда, которым разрешены запросы к API (через запятую)
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

# Тестовая "оплата" (кнопка "Оплатить тестово"). В production всегда выключена.
ENABLE_TEST_PAYMENTS = os.getenv("ENABLE_TEST_PAYMENTS", "false").lower() == "true" and not IS_PRODUCTION

# Логирование SQL выводит параметры запросов (email, хеши паролей), поэтому по умолчанию выключено
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"

TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "")
# Сколько живёт ссылка привязки Telegram
TELEGRAM_LINK_TTL_MINUTES = 15
