#!/bin/bash

# Скрипт для автоматического деплоя Mind Bot на Selectel VPS
# Использование: ./deploy.sh

set -e  # Остановка при ошибке

echo "🚀 Начинаем деплой Mind Bot на Selectel..."

# Проверяем, что мы в корне проекта
if [ ! -f "main.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из корня проекта"
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден. Создайте его на основе env_example.txt"
    echo "cp env_example.txt .env"
    echo "nano .env"
    exit 1
fi

echo "✅ Проверки пройдены"

# Создаем systemd сервис
echo "📝 Создание systemd сервиса..."

sudo tee /etc/systemd/system/mind_bot.service > /dev/null <<EOF
[Unit]
Description=Mind Bot Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd сервис создан"

# Перезагружаем systemd и запускаем сервис
echo "🔄 Запуск сервиса..."

sudo systemctl daemon-reload
sudo systemctl enable mind_bot
sudo systemctl start mind_bot

# Проверяем статус
echo "📊 Проверка статуса сервиса..."
sleep 3

if sudo systemctl is-active --quiet mind_bot; then
    echo "✅ Mind Bot успешно запущен!"
    echo "📋 Статус:"
    sudo systemctl status mind_bot --no-pager -l
else
    echo "❌ Ошибка запуска сервиса"
    echo "📋 Логи:"
    sudo journalctl -u mind_bot -n 20 --no-pager
    exit 1
fi

echo ""
echo "🎉 Деплой завершен успешно!"
echo ""
echo "📋 Полезные команды:"
echo "  Просмотр логов: sudo journalctl -u mind_bot -f"
echo "  Остановка бота: sudo systemctl stop mind_bot"
echo "  Перезапуск: sudo systemctl restart mind_bot"
echo "  Статус: sudo systemctl status mind_bot"
echo ""
echo "🔗 Бот готов к работе!" 