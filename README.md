# 🧠 Mind Bot - Телеграм-бот для развития креативного мышления

Телеграм-бот для курса по развитию креативного мышления с функциями тестирования, ИИ-помощника и системы напоминаний.

## ✨ Функции

- 📚 **Тест-квиз** - Проверка знаний по модулям курса
- 👁 **Тест на внимание** - Тренировка концентрации
- ⚡ **Тест на скорость** - Быстрые математические примеры
- 🧠 **Игры для мозга** - Логические задачи и последовательности
- 🤖 **ИИ-помощник** - Ответы на вопросы по курсу (GigaChat)
- ⏰ **Система напоминаний** - Настраиваемые уведомления

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/mind_bot.git
cd mind_bot
```

### 2. Установка зависимостей

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
# Telegram Bot Token (получите у @BotFather)
BOT_TOKEN=your_telegram_bot_token_here

# GigaChat Authorization Key (получите на https://developers.sber.ru/portal/products/gigachat)
GIGACHAT_AUTH_KEY=your_gigachat_authorization_key_here

# Database URL (опционально)
DATABASE_URL=sqlite:///mind_bot.db
```

### 4. Запуск бота

```bash
python main.py
```

## 🛠 Установка на сервер

### 🚀 Автоматический деплой (Рекомендуется)

**Одной командой на Ubuntu 24.04 LTS:**

```bash
# Скачиваем скрипт автоматического деплоя
wget https://raw.githubusercontent.com/your-username/mind_bot/main/auto_deploy.sh
chmod +x auto_deploy.sh

# Запускаем автоматический деплой
./auto_deploy.sh https://github.com/your-username/mind_bot.git YOUR_BOT_TOKEN YOUR_GIGACHAT_KEY
```

**Пример:**

```bash
./auto_deploy.sh https://github.com/username/mind_bot.git 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz your_gigachat_key_here
```

**Что делает автоматический скрипт:**

- ✅ Обновляет систему
- ✅ Устанавливает все зависимости
- ✅ Клонирует репозиторий
- ✅ Создает виртуальное окружение
- ✅ Настраивает переменные окружения
- ✅ Создает systemd сервис
- ✅ Запускает бота
- ✅ Создает скрипты управления
- ✅ Проверяет работоспособность

### 📋 Ручная установка

#### Selectel VPS

1. **Подключение к серверу:**

```bash
ssh root@your-server-ip
```

2. **Обновление системы:**

```bash
apt update && apt upgrade -y
```

3. **Установка Python и зависимостей:**

```bash
apt install python3 python3-pip python3-venv git -y
```

4. **Клонирование проекта:**

```bash
git clone https://github.com/your-username/mind_bot.git
cd mind_bot
```

5. **Создание виртуального окружения:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. **Настройка переменных окружения:**

```bash
cp env_example.txt .env
nano .env  # Отредактируйте файл с вашими ключами
```

7. **Создание systemd сервиса:**

```bash
sudo nano /etc/systemd/system/mind_bot.service
```

Содержимое файла:

```ini
[Unit]
Description=Mind Bot Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/mind_bot
Environment=PATH=/root/mind_bot/venv/bin
ExecStart=/root/mind_bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

8. **Запуск сервиса:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable mind_bot
sudo systemctl start mind_bot
sudo systemctl status mind_bot
```

## 🔧 Конфигурация

### Получение Telegram Bot Token

1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен

### Получение GigaChat Authorization Key

1. Зайдите на https://developers.sber.ru/portal/products/gigachat
2. Зарегистрируйтесь как разработчик
3. Создайте приложение
4. Получите Authorization key

## 📊 База данных

Бот использует SQLite для хранения:

- Пользователей и их настроек
- Результатов тестов
- Взаимодействий с ИИ

## 🔄 Обновление бота

### Автоматическое обновление

```bash
# Используйте созданный скрипт
mind_bot_update
```

### Ручное обновление

```bash
# На сервере
cd mind_bot
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart mind_bot
```

## 📝 Логи

### Автоматический просмотр логов

```bash
# Используйте созданный скрипт
mind_bot_logs
```

### Ручной просмотр логов

```bash
sudo journalctl -u mind_bot -f
```

## 🎮 Управление ботом

После автоматического деплоя доступны команды:

```bash
mind_bot_logs      # Просмотр логов в реальном времени
mind_bot_restart   # Перезапуск бота
mind_bot_update    # Обновление из GitHub
mind_bot_stop      # Остановка бота
mind_bot_start     # Запуск бота
```

## 📁 Структура проекта

```
mind_bot/
├── ai/                    # ИИ модули
│   ├── api_client.py     # GigaChat API клиент
│   ├── context_manager.py # Управление контекстом
│   └── ai_curator.py     # Контекст курса
├── data/                 # Данные
│   ├── messages.py       # Тексты сообщений
│   └── quiz_data.py      # Данные тестов
├── handlers/             # Обработчики
│   ├── start.py         # Главное меню
│   ├── quiz.py          # Тест-квиз
│   ├── attention.py     # Тест на внимание
│   ├── speed.py         # Тест на скорость
│   ├── brain_games.py   # Игры для мозга
│   ├── ai_assistant.py  # ИИ помощник
│   └── reminders.py     # Напоминания
├── states/              # Состояния FSM
│   └── user_states.py   # Определения состояний
├── utils/               # Утилиты
│   ├── database.py      # База данных
│   └── scheduler.py     # Планировщик
├── docs/                # Документация
│   ├── architecture.md  # Архитектура проекта
│   ├── user_stories.md  # Пользовательские сценарии
│   └── sequence_diagrams.md # Диаграммы последовательности
├── main.py              # Главный файл
├── config.py            # Конфигурация
├── requirements.txt     # Зависимости
├── auto_deploy.sh       # Автоматический деплой
├── deploy.sh            # Ручной деплой
└── README.md           # Документация
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License

## 🆘 Поддержка

Если у вас возникли проблемы:

1. Проверьте логи: `mind_bot_logs` или `sudo journalctl -u mind_bot -f`
2. Убедитесь, что все переменные окружения настроены
3. Проверьте подключение к интернету
4. Создайте Issue в GitHub

## 🎯 Планы развития

- [ ] Добавление новых типов тестов
- [ ] Интеграция с другими ИИ (YandexGPT, Claude)
- [ ] Веб-панель администратора
- [ ] Экспорт результатов в PDF
- [ ] Многоязычная поддержка
