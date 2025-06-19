# 🔄 Диаграммы последовательности - Mind Bot

## 📱 Основные сценарии взаимодействия

### 1. Запуск бота и навигация

```mermaid
sequenceDiagram
    participant U as User
    participant T as Telegram
    participant B as Bot
    participant DB as Database

    U->>T: /start
    T->>B: Message(chat_id, text="/start")
    B->>DB: get_user(chat_id)
    alt User exists
        DB-->>B: user_data
    else New user
        B->>DB: create_user(chat_id, username, name)
        DB-->>B: new_user_data
    end
    B->>B: generate_main_menu()
    B->>T: send_message(chat_id, welcome_text, keyboard)
    T->>U: Main menu with buttons

    U->>T: Click "📚 Тест-квиз"
    T->>B: CallbackQuery(chat_id, data="quiz")
    B->>B: set_state(QuizState.selecting_topic)
    B->>T: send_message(chat_id, topic_selection, keyboard)
    T->>U: Topic selection menu
```

### 2. Прохождение тест-квиза

```mermaid
sequenceDiagram
    participant U as User
    participant T as Telegram
    participant B as Bot
    participant DB as Database
    participant QD as QuizData

    U->>T: Select topic "Основы мышления"
    T->>B: CallbackQuery(chat_id, data="topic_basics")
    B->>QD: get_quiz_questions("basics")
    QD-->>B: questions_list
    B->>B: set_state(QuizState.testing)
    B->>B: start_quiz(questions)
    B->>T: send_message(chat_id, question_1, keyboard)
    T->>U: Question with options

    U->>T: Select answer "B"
    T->>B: CallbackQuery(chat_id, data="answer_1")
    B->>B: check_answer(question_1, "B")
    B->>B: next_question()
    B->>T: send_message(chat_id, question_2, keyboard)
    T->>U: Next question

    Note over U,B: Continue until all questions answered

    B->>B: calculate_results()
    B->>DB: save_test_result(user_id, results)
    DB-->>B: saved
    B->>B: set_state(QuizState.results)
    B->>T: send_message(chat_id, results_summary, keyboard)
    T->>U: Test results with analysis
```

### 3. Взаимодействие с ИИ помощником

```mermaid
sequenceDiagram
    participant U as User
    participant T as Telegram
    participant B as Bot
    participant AI as GigaChat API
    participant CM as ContextManager
    participant DB as Database

    U->>T: Click "🤖 ИИ помощник"
    T->>B: CallbackQuery(chat_id, data="ai_assistant")
    B->>B: set_state(AIState.waiting_question)
    B->>T: send_message(chat_id, ai_welcome, keyboard)
    T->>U: AI assistant welcome

    U->>T: "Что такое креативное мышление?"
    T->>B: Message(chat_id, text="Что такое креативное мышление?")
    B->>B: set_state(AIState.processing)
    B->>T: send_message(chat_id, "🤔 Думаю...")
    T->>U: Processing indicator

    B->>CM: get_context()
    CM-->>B: course_context
    B->>AI: send_request(question, context)
    AI-->>B: ai_response

    B->>DB: save_ai_interaction(user_id, question, response)
    DB-->>B: saved
    B->>B: set_state(AIState.showing_answer)
    B->>T: send_message(chat_id, ai_response, rating_keyboard)
    T->>U: AI answer with rating buttons

    U->>T: Click "⭐⭐⭐⭐⭐"
    T->>B: CallbackQuery(chat_id, data="rate_5")
    B->>DB: save_rating(interaction_id, 5)
    DB-->>B: saved
    B->>T: send_message(chat_id, "Спасибо за оценку!")
    T->>U: Thank you message
```

### 4. Система напоминаний

```mermaid
sequenceDiagram
    participant S as Scheduler
    participant B as Bot
    participant T as Telegram
    participant U as User
    participant DB as Database

    Note over S: Daily at 9:00 AM
    S->>DB: get_users_with_reminders()
    DB-->>S: users_list

    loop For each user
        S->>DB: get_reminder_settings(user_id)
        DB-->>S: settings
        alt Should send reminder
            S->>B: send_reminder(user_id, message)
            B->>T: send_message(user_id, reminder_text)
            T->>U: Reminder notification
            B->>DB: log_reminder_sent(user_id)
            DB-->>B: logged
        end
    end

    Note over U,B: User can configure reminders
    U->>T: Click "⏰ Напоминания"
    T->>B: CallbackQuery(chat_id, data="reminders")
    B->>B: set_state(ReminderState.configuring)
    B->>T: send_message(chat_id, reminder_menu, keyboard)
    T->>U: Reminder settings menu

    U->>T: Select "Ежедневно"
    T->>B: CallbackQuery(chat_id, data="daily")
    B->>DB: update_reminder_settings(user_id, "daily")
    DB-->>B: updated
    B->>T: send_message(chat_id, "Напоминания настроены!")
    T->>U: Confirmation message
```

### 5. Обработка команд во время тестов

```mermaid
sequenceDiagram
    participant U as User
    participant T as Telegram
    participant B as Bot
    participant DB as Database

    Note over U,B: User is in the middle of a test
    U->>T: /start
    T->>B: Message(chat_id, text="/start")
    B->>B: check_current_state(user_id)
    B->>B: clear_current_test(user_id)
    B->>B: set_state(MainState.menu)
    B->>DB: save_test_progress(user_id, "interrupted")
    DB-->>B: saved
    B->>T: send_message(chat_id, welcome_back, main_keyboard)
    T->>U: Main menu (test interrupted)

    Note over U,B: User continues with new test
    U->>T: Click "⚡ Тест на скорость"
    T->>B: CallbackQuery(chat_id, data="speed_test")
    B->>B: set_state(SpeedState.testing)
    B->>T: send_message(chat_id, speed_welcome, keyboard)
    T->>U: Speed test interface
```

### 6. Обработка ошибок

```mermaid
sequenceDiagram
    participant U as User
    participant T as Telegram
    participant B as Bot
    participant AI as GigaChat API
    participant DB as Database

    U->>T: Ask AI question
    T->>B: Message(chat_id, text="question")
    B->>AI: send_request(question)

    alt API Error
        AI-->>B: Error: "Service unavailable"
        B->>DB: log_error("ai_api_error", error_details)
        DB-->>B: logged
        B->>T: send_message(chat_id, "Извините, ИИ временно недоступен. Попробуйте позже.")
        T->>U: Error message
    else Network Error
        B->>B: catch_timeout_exception()
        B->>DB: log_error("network_timeout", error_details)
        DB-->>B: logged
        B->>T: send_message(chat_id, "Проблемы с соединением. Проверьте интернет.")
        T->>U: Network error message
    else Success
        AI-->>B: ai_response
        B->>T: send_message(chat_id, ai_response, keyboard)
        T->>U: Normal response
    end
```

### 7. Инициализация и запуск бота

```mermaid
sequenceDiagram
    participant S as System
    participant B as Bot
    participant DB as Database
    participant AI as GigaChat API
    participant T as Telegram API

    S->>B: python main.py
    B->>B: load_config()
    B->>B: validate_environment()

    alt Config valid
        B->>DB: initialize_database()
        DB-->>B: database_ready
        B->>AI: test_connection()
        AI-->>B: connection_ok
        B->>T: test_webhook()
        T-->>B: webhook_ok
        B->>B: setup_handlers()
        B->>B: start_polling()
        B->>S: Bot started successfully
    else Config invalid
        B->>S: Error: Missing environment variables
        S->>S: Exit with error code
    end
```

## 🔧 Технические детали

### Состояния FSM (Finite State Machine)

```mermaid
stateDiagram-v2
    [*] --> MainMenu

    MainMenu --> QuizSelecting: Выбрать тест-квиз
    MainMenu --> AttentionTesting: Выбрать тест внимания
    MainMenu --> SpeedTesting: Выбрать тест скорости
    MainMenu --> BrainGames: Выбрать игры для мозга
    MainMenu --> AIWaiting: Выбрать ИИ помощника
    MainMenu --> ReminderConfig: Настроить напоминания

    QuizSelecting --> QuizTesting: Выбрать тему
    QuizTesting --> QuizResults: Завершить тест
    QuizResults --> MainMenu: Вернуться в меню

    AttentionTesting --> AttentionResults: Завершить тест
    AttentionResults --> MainMenu: Вернуться в меню

    SpeedTesting --> SpeedResults: Завершить тест
    SpeedResults --> MainMenu: Вернуться в меню

    BrainGames --> BrainResults: Завершить игру
    BrainResults --> MainMenu: Вернуться в меню

    AIWaiting --> AIProcessing: Задать вопрос
    AIProcessing --> AIShowing: Получить ответ
    AIShowing --> AIRating: Оценить ответ
    AIRating --> AIWaiting: Задать еще вопрос
    AIRating --> MainMenu: Вернуться в меню

    ReminderConfig --> MainMenu: Сохранить настройки

    MainMenu --> [*]: /start, /help, /menu
```

### Поток данных в базе

```mermaid
flowchart TD
    A[User Action] --> B[Handler]
    B --> C[State Manager]
    C --> D[Database]
    D --> E[SQLite Tables]

    E --> F[users]
    E --> G[test_results]
    E --> H[ai_interactions]
    E --> I[reminder_settings]

    B --> J[External APIs]
    J --> K[Telegram API]
    J --> L[GigaChat API]

    B --> M[File System]
    M --> N[quiz_data.py]
    M --> O[messages.py]
    M --> P[ai_curator.py]

    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style D fill:#fff3e0
    style J fill:#e8f5e8
```
