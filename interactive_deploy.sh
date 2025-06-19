#!/bin/bash

# 🚀 Интерактивный деплой Mind Bot на Ubuntu 24.04 LTS
# Использование: ./interactive_deploy.sh

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Функция для безопасного ввода
read_secret() {
    local prompt="$1"
    local var_name="$2"
    
    echo -n "$prompt: "
    read -s "$var_name"
    echo
}

print_success "🚀 Интерактивный деплой Mind Bot..."
echo ""

# Запрос данных у пользователя
print_info "Введите данные для деплоя:"
echo ""

# GitHub репозиторий
echo -n "GitHub репозиторий (по умолчанию: https://github.com/MichaelFr2/mind_bot.git): "
read GITHUB_REPO_URL
GITHUB_REPO_URL=${GITHUB_REPO_URL:-"https://github.com/MichaelFr2/mind_bot.git"}

# Telegram Bot Token
read_secret "Telegram Bot Token" BOT_TOKEN

# GigaChat Authorization Key
read_secret "GigaChat Authorization Key" GIGACHAT_KEY

echo ""
print_info "Проверка введенных данных:"
print_info "Репозиторий: $GITHUB_REPO_URL"
print_info "Bot Token: ${BOT_TOKEN:0:10}..."
print_info "GigaChat Key: ${GIGACHAT_KEY:0:10}..."

echo ""
echo -n "Все данные корректны? (y/N): "
read CONFIRM

if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    print_error "Деплой отменен"
    exit 1
fi

PROJECT_NAME="mind_bot"

print_success "🚀 Начинаем автоматический деплой Mind Bot..."
print_info "Репозиторий: $GITHUB_REPO_URL"
print_info "Проект: $PROJECT_NAME"

# 1. Обновление системы
print_info "📦 Обновление системы..."
apt update -qq
apt upgrade -y -qq
print_success "Система обновлена"

# 2. Установка необходимых пакетов
print_info "🔧 Установка необходимых пакетов..."
apt install -y -qq python3 python3-pip python3-venv git curl wget nano htop
print_success "Пакеты установлены"

# 3. Проверка и удаление старой версии
if [ -d "/root/$PROJECT_NAME" ]; then
    print_warning "Найдена старая версия проекта. Удаляем..."
    rm -rf "/root/$PROJECT_NAME"
fi

# 4. Клонирование репозитория
print_info "📥 Клонирование репозитория..."
cd /root
git clone "$GITHUB_REPO_URL" "$PROJECT_NAME" -q
cd "$PROJECT_NAME"
print_success "Репозиторий склонирован"

# 5. Создание виртуального окружения
print_info "🐍 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
print_success "Виртуальное окружение создано"

# 6. Установка зависимостей
print_info "📚 Установка зависимостей..."
pip install -r requirements.txt -q
print_success "Зависимости установлены"

# 7. Создание .env файла
print_info "⚙️  Настройка переменных окружения..."
cat > .env << EOF
# Telegram Bot Token
BOT_TOKEN=$BOT_TOKEN

# GigaChat Authorization Key
GIGACHAT_AUTH_KEY=$GIGACHAT_KEY

# Database URL
DATABASE_URL=sqlite:///mind_bot.db
EOF
print_success "Переменные окружения настроены"

# 8. Тестирование конфигурации
print_info "🧪 Тестирование конфигурации..."
if python -c "import config; print('✅ Конфигурация корректна')" 2>/dev/null; then
    print_success "Конфигурация проверена"
else
    print_warning "Конфигурация не проверена, продолжаем..."
fi

# 9. Остановка старого сервиса если существует
if systemctl is-active --quiet mind_bot 2>/dev/null; then
    print_info "🛑 Остановка старого сервиса..."
    systemctl stop mind_bot
fi

# 10. Создание systemd сервиса
print_info "🔧 Создание systemd сервиса..."
cat > /etc/systemd/system/mind_bot.service << EOF
[Unit]
Description=Mind Bot Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/$PROJECT_NAME
Environment=PATH=/root/$PROJECT_NAME/venv/bin
ExecStart=/root/$PROJECT_NAME/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
print_success "Systemd сервис создан"

# 11. Настройка прав доступа
print_info "🔐 Настройка прав доступа..."
chmod +x /root/$PROJECT_NAME/main.py
chown -R root:root /root/$PROJECT_NAME
print_success "Права доступа настроены"

# 12. Запуск сервиса
print_info "🚀 Запуск сервиса..."
systemctl daemon-reload
systemctl enable mind_bot
systemctl start mind_bot

# 13. Ожидание запуска
print_info "⏳ Ожидание запуска сервиса..."
sleep 5

# 14. Проверка статуса
if systemctl is-active --quiet mind_bot; then
    print_success "🎉 Mind Bot успешно запущен!"
    
    # Показываем статус
    echo ""
    print_info "📊 Статус сервиса:"
    systemctl status mind_bot --no-pager -l
    
    # Показываем последние логи
    echo ""
    print_info "📋 Последние логи:"
    journalctl -u mind_bot -n 10 --no-pager
    
else
    print_error "❌ Ошибка запуска сервиса"
    print_info "📋 Логи ошибок:"
    journalctl -u mind_bot -n 20 --no-pager
    exit 1
fi

# 15. Создание скриптов управления
print_info "📝 Создание скриптов управления..."

# Скрипт для просмотра логов
cat > /usr/local/bin/mind_bot_logs << 'EOF'
#!/bin/bash
journalctl -u mind_bot -f
EOF

# Скрипт для перезапуска
cat > /usr/local/bin/mind_bot_restart << 'EOF'
#!/bin/bash
systemctl restart mind_bot
echo "Mind Bot перезапущен"
systemctl status mind_bot --no-pager
EOF

# Скрипт для обновления
cat > /usr/local/bin/mind_bot_update << 'EOF'
#!/bin/bash
cd /root/mind_bot
git pull
systemctl restart mind_bot
echo "Mind Bot обновлен и перезапущен"
systemctl status mind_bot --no-pager
EOF

# Скрипт для остановки
cat > /usr/local/bin/mind_bot_stop << 'EOF'
#!/bin/bash
systemctl stop mind_bot
echo "Mind Bot остановлен"
EOF

# Скрипт для запуска
cat > /usr/local/bin/mind_bot_start << 'EOF'
#!/bin/bash
systemctl start mind_bot
echo "Mind Bot запущен"
systemctl status mind_bot --no-pager
EOF

# Делаем скрипты исполняемыми
chmod +x /usr/local/bin/mind_bot_*

print_success "Скрипты управления созданы"

# 16. Финальная информация
echo ""
print_success "🎉 Деплой завершен успешно!"
echo ""
print_info "📋 Полезные команды:"
echo "  Просмотр логов: mind_bot_logs"
echo "  Перезапуск: mind_bot_restart"
echo "  Обновление: mind_bot_update"
echo "  Остановка: mind_bot_stop"
echo "  Запуск: mind_bot_start"
echo "  Статус: systemctl status mind_bot"
echo ""
print_info "🔗 Бот готов к работе!"
print_info "Найдите бота в Telegram и отправьте /start"
echo ""
print_info "📊 Мониторинг:"
echo "  Логи в реальном времени: journalctl -u mind_bot -f"
echo "  Использование ресурсов: htop"
echo "  Статус сервиса: systemctl status mind_bot" 