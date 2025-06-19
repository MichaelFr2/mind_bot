import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# GigaChat Authorization Key
GIGACHAT_AUTH_KEY = os.getenv('GIGACHAT_AUTH_KEY')

# Database URL
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///mind_bot.db')

# Logging level
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# API timeout
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))

# Max retries for API calls
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# Проверка обязательных переменных
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

if not GIGACHAT_AUTH_KEY:
    raise ValueError("GIGACHAT_AUTH_KEY не найден в переменных окружения")

# Scheduler
SCHEDULER_TIMEZONE = "Europe/Moscow" 