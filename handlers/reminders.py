from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from states.user_states import UserStates
from data.messages import REMINDER_SETUP_MESSAGE, REMINDER_CONFIRMED_MESSAGE, REMINDER_CANCELLED_MESSAGE
from utils.database import Database

class RemindersHandler:
    def __init__(self, database: Database):
        self.database = database
    
    async def show_reminder_menu(self, message: types.Message, state: FSMContext):
        """Показ меню настроек напоминаний"""
        await state.set_state(UserStates.REMINDER_SETUP)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Раз в день", callback_data="reminder_daily")],
            [InlineKeyboardButton(text="📅 Раз в 2 дня", callback_data="reminder_2days")],
            [InlineKeyboardButton(text="📅 По понедельникам и четвергам", callback_data="reminder_mon_thu")],
            [InlineKeyboardButton(text="📅 Только по выходным", callback_data="reminder_weekends")],
            [InlineKeyboardButton(text="❌ Отменить все напоминания", callback_data="reminder_cancel")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
        ])
        
        await message.answer(REMINDER_SETUP_MESSAGE, reply_markup=keyboard)
    
    async def handle_reminder_callback(self, callback: types.CallbackQuery, state: FSMContext):
        """Обработка callback кнопок напоминаний"""
        action = callback.data
        
        if action == "back_to_menu":
            await state.clear()
            await callback.message.delete()
            await callback.answer()
            return "back_to_menu"
        
        elif action == "reminder_cancel":
            # Отключаем напоминания
            await self.database.set_reminder(
                user_id=callback.from_user.id,
                frequency="none",
                enabled=False
            )
            await callback.message.edit_text(REMINDER_CANCELLED_MESSAGE)
            await callback.answer()
        
        else:
            # Устанавливаем напоминания
            frequency_map = {
                "reminder_daily": "daily",
                "reminder_2days": "2days", 
                "reminder_mon_thu": "mon_thu",
                "reminder_weekends": "weekends"
            }
            
            frequency = frequency_map.get(action, "daily")
            
            await self.database.set_reminder(
                user_id=callback.from_user.id,
                frequency=frequency,
                enabled=True
            )
            
            await callback.message.edit_text(REMINDER_CONFIRMED_MESSAGE)
            await callback.answer()
        
        await state.clear() 