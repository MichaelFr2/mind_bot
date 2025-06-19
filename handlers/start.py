from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from states.user_states import UserStates
from data.messages import WELCOME_MESSAGE, HELP_MESSAGE
from utils.database import Database

class StartHandler:
    def __init__(self, database: Database):
        self.database = database
    
    async def start_command(self, message: types.Message, state: FSMContext):
        """Обработка команды /start"""
        # Сбрасываем состояние
        await state.clear()
        
        # Добавляем пользователя в базу
        await self.database.add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        # Показываем главное меню
        await self.show_main_menu(message)
    
    async def show_main_menu(self, message: types.Message):
        """Показ главного меню"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Тест-квиз", callback_data="quiz"),
                InlineKeyboardButton(text="👁 Тест на внимание", callback_data="attention")
            ],
            [
                InlineKeyboardButton(text="⚡ Тест на скорость", callback_data="speed"),
                InlineKeyboardButton(text="🧠 Разминка мозга", callback_data="brain_games")
            ],
            [
                InlineKeyboardButton(text="🤖 ИИ помощник", callback_data="ai_assistant"),
                InlineKeyboardButton(text="⏰ Напоминания", callback_data="reminders")
            ],
            [
                InlineKeyboardButton(text="❓ Помощь", callback_data="help")
            ]
        ])
        
        await message.answer(WELCOME_MESSAGE, reply_markup=keyboard)
    
    async def help_command(self, message: types.Message, state: FSMContext):
        """Обработка команды /help"""
        await state.clear()
        await message.answer(HELP_MESSAGE, parse_mode="Markdown")
    
    async def menu_command(self, message: types.Message, state: FSMContext):
        """Обработка команды /menu"""
        await state.set_state(UserStates.MAIN_MENU)
        await self.show_main_menu(message)
    
    async def handle_callback(self, callback: types.CallbackQuery, state: FSMContext):
        """Обработка callback кнопок главного меню"""
        action = callback.data
        
        if action == "help":
            await callback.message.edit_text(HELP_MESSAGE, parse_mode="Markdown")
            await callback.answer()
        else:
            # Передаем управление другим обработчикам
            await callback.answer()
            return action  # Возвращаем действие для обработки в main.py 