import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from config import BOT_TOKEN
from handlers.start import StartHandler
from handlers.quiz import QuizHandler
from handlers.attention import AttentionHandler
from handlers.speed import SpeedHandler
from handlers.brain_games import BrainGamesHandler
from handlers.ai_assistant import AIAssistantHandler
from handlers.reminders import RemindersHandler
from utils.database import Database
from utils.scheduler import Scheduler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotApp:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.database = Database()
        self.scheduler = Scheduler(self.bot, self.database)
        
        # Инициализация обработчиков
        self.start_handler = StartHandler(self.database)
        self.quiz_handler = QuizHandler(self.database)
        self.attention_handler = AttentionHandler(self.database)
        self.speed_handler = SpeedHandler(self.database)
        self.brain_games_handler = BrainGamesHandler(self.database)
        self.ai_assistant_handler = AIAssistantHandler(self.database)
        self.reminders_handler = RemindersHandler(self.database)
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        # Команды
        self.dp.message.register(self.start_handler.start_command, Command("start"))
        self.dp.message.register(self.start_handler.help_command, Command("help"))
        self.dp.message.register(self.start_handler.menu_command, Command("menu"))
        
        # Обработка callback'ов главного меню
        self.dp.callback_query.register(self.handle_main_menu_callback, lambda c: c.data in [
            "quiz", "attention", "speed", "brain_games", "ai_assistant", "reminders", "help", "back_to_menu"
        ])
        
        # Обработка callback'ов квиза
        self.dp.callback_query.register(self.quiz_handler.start_quiz, lambda c: c.data.startswith("quiz_module_"))
        self.dp.callback_query.register(self.quiz_handler.handle_answer, lambda c: c.data.startswith("quiz_answer_"))
        
        # Обработка callback'ов теста на внимание
        self.dp.callback_query.register(self.attention_handler.handle_answer, lambda c: c.data.startswith("attention_answer_"))
        
        # Обработка callback'ов теста на скорость
        self.dp.callback_query.register(self.speed_handler.handle_answer, lambda c: c.data.startswith("speed_answer_"))
        
        # Обработка callback'ов игр для мозга
        self.dp.callback_query.register(self.brain_games_handler.start_brain_game, lambda c: c.data.startswith("brain_game_"))
        self.dp.callback_query.register(self.brain_games_handler.handle_game_answer, lambda c: c.data.startswith("brain_answer_"))
        
        # Обработка callback'ов ИИ помощника
        self.dp.callback_query.register(self.ai_assistant_handler.handle_ai_feedback, lambda c: c.data.startswith("ai_"))
        
        # Обработка callback'ов напоминаний
        self.dp.callback_query.register(self.reminders_handler.handle_reminder_callback, lambda c: c.data.startswith("reminder_"))
        
        # Обработка текстовых сообщений (для ИИ помощника)
        self.dp.message.register(self.ai_assistant_handler.handle_ai_question)
    
    async def handle_main_menu_callback(self, callback: types.CallbackQuery, state: FSMContext):
        """Обработка callback'ов главного меню"""
        action = callback.data
        
        if action == "back_to_menu":
            await state.clear()
            await self.start_handler.show_main_menu(callback.message)
            await callback.answer()
            return
        
        # Обрабатываем действия главного меню
        if action == "quiz":
            await self.quiz_handler.show_quiz_selection(callback.message, state)
        elif action == "attention":
            await self.attention_handler.start_attention_test(callback.message, state)
        elif action == "speed":
            await self.speed_handler.start_speed_test(callback.message, state)
        elif action == "brain_games":
            await self.brain_games_handler.show_brain_games_menu(callback.message, state)
        elif action == "ai_assistant":
            await self.ai_assistant_handler.start_ai_chat(callback.message, state)
        elif action == "reminders":
            await self.reminders_handler.show_reminder_menu(callback.message, state)
        elif action == "help":
            await self.start_handler.help_command(callback.message, state)
        
        await callback.answer()
    
    async def start(self):
        """Запуск бота"""
        logger.info("Запуск бота...")
        
        # Инициализация базы данных
        await self.database.init_db()
        
        # Запуск планировщика напоминаний
        await self.scheduler.start()
        
        try:
            await self.dp.start_polling(self.bot)
        finally:
            await self.scheduler.stop()
            await self.bot.session.close()

if __name__ == "__main__":
    app = BotApp()
    asyncio.run(app.start()) 