# 🏗 Архитектура Mind Bot

## 📊 Структура проекта

```mermaid
graph TB
    A[main.py] --> B[handlers/]
    A --> C[states/]
    A --> D[utils/]
    A --> E[ai/]
    A --> F[data/]

    B --> B1[start.py]
    B --> B2[quiz.py]
    B --> B3[attention.py]
    B --> B4[speed.py]
    B --> B5[brain_games.py]
    B --> B6[ai_assistant.py]
    B --> B7[reminders.py]

    C --> C1[user_states.py]

    D --> D1[database.py]
    D --> D2[scheduler.py]

    E --> E1[api_client.py]
    E --> E2[context_manager.py]
    E --> E3[ai_curator.py]

    F --> F1[messages.py]
    F --> F2[quiz_data.py]

    style A fill:#ff9999
    style B fill:#99ccff
    style C fill:#99ff99
    style D fill:#ffcc99
    style E fill:#cc99ff
    style F fill:#ffff99
```

## 🔄 Поток данных

```mermaid
flowchart LR
    A[Telegram User] --> B[main.py]
    B --> C{Command Router}

    C --> D[Start Handler]
    C --> E[Quiz Handler]
    C --> F[Attention Handler]
    C --> G[Speed Handler]
    H --> I[Brain Games Handler]
    C --> J[AI Assistant Handler]
    C --> K[Reminders Handler]

    D --> L[Database]
    E --> L
    F --> L
    G --> L
    H --> L
    J --> L
    K --> L

    J --> M[GigaChat API]
    M --> N[Context Manager]
    N --> O[AI Curator]

    K --> P[Scheduler]
    P --> Q[Reminder Engine]

    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style M fill:#fff3e0
    style P fill:#e8f5e8
```

## 🎯 User Stories

### 👤 Основные пользовательские сценарии

```mermaid
journey
    title Пользовательский опыт Mind Bot
    section Регистрация и знакомство
      Открытие бота: 5: Пользователь
      Получение приветствия: 5: Пользователь
      Изучение меню: 4: Пользователь
    section Тестирование
      Выбор типа теста: 5: Пользователь
      Прохождение теста: 4: Пользователь
      Получение результатов: 5: Пользователь
      Анализ ошибок: 4: Пользователь
    section ИИ помощник
      Задавание вопроса: 5: Пользователь
      Получение ответа: 5: Пользователь
      Оценка полезности: 3: Пользователь
    section Напоминания
      Настройка расписания: 4: Пользователь
      Получение уведомлений: 4: Пользователь
      Изменение настроек: 3: Пользователь
```

## 🧠 Состояния пользователя (FSM)

```mermaid
stateDiagram-v2
    [*] --> MainMenu

    MainMenu --> QuizTest: Выбрать тест-квиз
    MainMenu --> AttentionTest: Выбрать тест внимания
    MainMenu --> SpeedTest: Выбрать тест скорости
    MainMenu --> BrainGames: Выбрать игры для мозга
    MainMenu --> AIAssistant: Выбрать ИИ помощника
    MainMenu --> Reminders: Настроить напоминания

    QuizTest --> QuizQuestion: Начать тест
    QuizQuestion --> QuizQuestion: Ответить на вопрос
    QuizQuestion --> QuizResult: Завершить тест
    QuizResult --> MainMenu: Вернуться в меню

    AttentionTest --> AttentionQuestion: Начать тест
    AttentionQuestion --> AttentionQuestion: Ответить на вопрос
    AttentionQuestion --> AttentionResult: Завершить тест
    AttentionResult --> MainMenu: Вернуться в меню

    SpeedTest --> SpeedQuestion: Начать тест
    SpeedQuestion --> SpeedQuestion: Ответить на вопрос
    SpeedQuestion --> SpeedResult: Завершить тест
    SpeedResult --> MainMenu: Вернуться в меню

    BrainGames --> BrainGameTask: Начать игру
    BrainGameTask --> BrainGameTask: Решить задачу
    BrainGameTask --> BrainGameResult: Завершить игру
    BrainGameResult --> MainMenu: Вернуться в меню

    AIAssistant --> AIQuestion: Задать вопрос
    AIQuestion --> AIAnswer: Получить ответ
    AIAnswer --> AIRating: Оценить ответ
    AIRating --> AIAssistant: Задать еще вопрос
    AIRating --> MainMenu: Вернуться в меню

    Reminders --> ReminderSettings: Настроить
    ReminderSettings --> MainMenu: Сохранить настройки

    MainMenu --> [*]: /start, /help, /menu
```

## 🗄 База данных

```mermaid
erDiagram
    USERS {
        int user_id PK
        string username
        string first_name
        string last_name
        datetime created_at
        datetime last_activity
        boolean is_active
    }

    TEST_RESULTS {
        int id PK
        int user_id FK
        string test_type
        int score
        int total_questions
        float accuracy
        int time_spent
        datetime completed_at
    }

    AI_INTERACTIONS {
        int id PK
        int user_id FK
        text question
        text answer
        int rating
        datetime created_at
    }

    REMINDER_SETTINGS {
        int id PK
        int user_id FK
        string frequency
        time reminder_time
        boolean is_active
        datetime created_at
    }

    USERS ||--o{ TEST_RESULTS : "has"
    USERS ||--o{ AI_INTERACTIONS : "has"
    USERS ||--o{ REMINDER_SETTINGS : "has"
```

## 🔧 Компонентная архитектура

```mermaid
graph TB
    subgraph "Telegram Bot Layer"
        A[main.py]
        B[Command Router]
        C[Message Handler]
    end

    subgraph "Business Logic Layer"
        D[Test Handlers]
        E[AI Assistant]
        F[Reminder System]
    end

    subgraph "Data Layer"
        G[Database]
        H[File Storage]
    end

    subgraph "External Services"
        I[GigaChat API]
        J[Telegram API]
    end

    subgraph "State Management"
        K[FSM States]
        L[User Context]
    end

    A --> B
    B --> C
    C --> D
    C --> E
    C --> F

    D --> G
    E --> G
    F --> G

    E --> I
    A --> J

    C --> K
    K --> L

    style A fill:#ff9999
    style D fill:#99ccff
    style E fill:#99ff99
    style F fill:#ffcc99
    style G fill:#cc99ff
    style I fill:#ffff99
```

## 📈 Метрики и мониторинг

```mermaid
graph LR
    A[User Actions] --> B[Event Logger]
    B --> C[Database]
    C --> D[Analytics]

    D --> E[User Engagement]
    D --> F[Test Performance]
    D --> G[AI Usage]
    D --> H[System Health]

    E --> I[Dashboard]
    F --> I
    G --> I
    H --> I

    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style D fill:#fff3e0
    style I fill:#e8f5e8
```

## 🚀 Деплой архитектура

```mermaid
graph TB
    subgraph "Development"
        A[Local Machine]
        B[Git Repository]
    end

    subgraph "Production"
        C[Selectel VPS]
        D[Systemd Service]
        E[Python Environment]
        F[Bot Process]
    end

    subgraph "External APIs"
        G[Telegram API]
        H[GigaChat API]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F

    F --> G
    F --> H

    style A fill:#e1f5fe
    style C fill:#f3e5f5
    style F fill:#fff3e0
    style G fill:#e8f5e8
    style H fill:#fff3e0
```
