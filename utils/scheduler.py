from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from typing import List, Dict, Any
from utils.database import Database
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class Scheduler:
    def __init__(self, bot, database: Database):
        self.bot = bot
        self.database = database
        self.scheduler = AsyncIOScheduler()
        
    async def start(self):
        """Запуск планировщика"""
        self.scheduler.start()
        self._setup_reminders()
    
    async def stop(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
    
    def _setup_reminders(self):
        """Настройка напоминаний"""
        # Ежедневные напоминания в 10:00
        self.scheduler.add_job(
            self._send_daily_reminders,
            CronTrigger(hour=10, minute=0),
            id='daily_reminders',
            replace_existing=True
        )
        
        # Напоминания по понедельникам и четвергам в 18:00
        self.scheduler.add_job(
            self._send_weekly_reminders,
            CronTrigger(day_of_week='mon,thu', hour=18, minute=0),
            id='weekly_reminders',
            replace_existing=True
        )
        
        # Напоминания по выходным в 12:00
        self.scheduler.add_job(
            self._send_weekend_reminders,
            CronTrigger(day_of_week='sat,sun', hour=12, minute=0),
            id='weekend_reminders',
            replace_existing=True
        )
    
    async def _send_daily_reminders(self):
        """Отправка ежедневных напоминаний"""
        users = await self.database.get_users_with_reminders()
        
        for user in users:
            if user['reminder_frequency'] in ['daily', 'once_a_day']:
                await self._send_reminder_message(user['user_id'])
    
    async def _send_weekly_reminders(self):
        """Отправка напоминаний по понедельникам и четвергам"""
        users = await self.database.get_users_with_reminders()
        
        for user in users:
            if user['reminder_frequency'] in ['mon_thu', 'twice_a_week']:
                await self._send_reminder_message(user['user_id'])
    
    async def _send_weekend_reminders(self):
        """Отправка напоминаний по выходным"""
        users = await self.database.get_users_with_reminders()
        
        for user in users:
            if user['reminder_frequency'] in ['weekends', 'weekend_only']:
                await self._send_reminder_message(user['user_id'])
    
    async def _send_reminder_message(self, user_id: int):
        """Отправка сообщения-напоминания"""
        reminder_messages = [
            "🧠 Привет! Не забывай прокачивать своё мышление! Готов к новым вызовам?",
            "💪 Время для тренировки мозга! Какой тест выберешь сегодня?",
            "🚀 Твой мозг ждёт новых задач! Загляни в помощник курса!",
            "🎯 Маленький шаг к большому мышлению! Пора заниматься!",
            "🌟 Развитие мышления - это путь к успеху! Продолжай движение!"
        ]
        
        import random
        message = random.choice(reminder_messages)
        
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                reply_markup=self._get_reminder_keyboard()
            )
        except Exception as e:
            print(f"Ошибка отправки напоминания пользователю {user_id}: {e}")
    
    def _get_reminder_keyboard(self):
        """Клавиатура для напоминаний"""
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
                InlineKeyboardButton(text="🤖 ИИ помощник", callback_data="ai_assistant")
            ]
        ])
        return keyboard 