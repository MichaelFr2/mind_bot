from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    # Основные состояния
    MAIN_MENU = State()
    
    # Состояния тестов
    QUIZ_SELECTION = State()
    QUIZ_IN_PROGRESS = State()
    ATTENTION_TEST = State()
    SPEED_TEST = State()
    BRAIN_GAMES_SELECTION = State()
    BRAIN_GAME_IN_PROGRESS = State()
    
    # Состояния настроек
    REMINDER_SETUP = State()
    
    # Состояния ИИ помощника
    AI_CHAT = State()          # Чат с ИИ
    AI_FEEDBACK = State()      # Обратная связь по ответу 