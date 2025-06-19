#!/bin/bash

# Скрипт для запуска Mind Bot

echo "🧠 Запуск Mind Bot..."

# Проверяем, существует ли виртуальное окружение
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "Создаю виртуальное окружение..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Проверяем, установлены ли зависимости
if ! python -c "import aiogram" 2>/dev/null; then
    echo "📦 Установка зависимостей..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден!"
    echo "Создайте файл .env на основе env_example.txt"
    echo "И добавьте ваши токены:"
    echo "  - BOT_TOKEN (от @BotFather)"
    echo "  - AI_API_KEY (от OpenAI)"
    exit 1
fi

# Запускаем бота
echo "🚀 Запуск бота..."
python main.py 