import sqlite3
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime

class Database:
    def __init__(self, db_path: str = "mind_bot.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Асинхронная инициализация базы данных"""
        await asyncio.get_event_loop().run_in_executor(
            None, self.init_database
        )
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reminder_frequency TEXT DEFAULT 'none',
                reminder_enabled BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Таблица результатов тестов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                test_type TEXT,
                score INTEGER,
                total_questions INTEGER,
                completion_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица взаимодействий с ИИ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question TEXT,
                answer TEXT,
                feedback INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def add_user(self, user_id: int, username: str = None, 
                      first_name: str = None, last_name: str = None):
        """Добавление нового пользователя"""
        await asyncio.get_event_loop().run_in_executor(
            None, self._add_user_sync, user_id, username, first_name, last_name
        )
    
    def _add_user_sync(self, user_id: int, username: str = None, 
                      first_name: str = None, last_name: str = None):
        """Синхронное добавление пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        
        conn.commit()
        conn.close()
    
    async def save_test_result(self, user_id: int, test_type: str, 
                             score: int, total_questions: int, 
                             completion_time: float = None):
        """Сохранение результата теста"""
        await asyncio.get_event_loop().run_in_executor(
            None, self._save_test_result_sync, user_id, test_type, 
            score, total_questions, completion_time
        )
    
    def _save_test_result_sync(self, user_id: int, test_type: str, 
                             score: int, total_questions: int, 
                             completion_time: float = None):
        """Синхронное сохранение результата теста"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO test_results (user_id, test_type, score, total_questions, completion_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, test_type, score, total_questions, completion_time))
        
        conn.commit()
        conn.close()
    
    async def save_ai_interaction(self, user_id: int, question: str, 
                                answer: str, feedback: int = None):
        """Сохранение взаимодействия с ИИ"""
        await asyncio.get_event_loop().run_in_executor(
            None, self._save_ai_interaction_sync, user_id, question, answer, feedback
        )
    
    def _save_ai_interaction_sync(self, user_id: int, question: str, 
                                answer: str, feedback: int = None):
        """Синхронное сохранение взаимодействия с ИИ"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_interactions (user_id, question, answer, feedback)
            VALUES (?, ?, ?, ?)
        ''', (user_id, question, answer, feedback))
        
        conn.commit()
        conn.close()
    
    async def set_reminder(self, user_id: int, frequency: str, enabled: bool = True):
        """Установка напоминаний для пользователя"""
        await asyncio.get_event_loop().run_in_executor(
            None, self._set_reminder_sync, user_id, frequency, enabled
        )
    
    def _set_reminder_sync(self, user_id: int, frequency: str, enabled: bool = True):
        """Синхронная установка напоминаний"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET reminder_frequency = ?, reminder_enabled = ?
            WHERE user_id = ?
        ''', (frequency, enabled, user_id))
        
        conn.commit()
        conn.close()
    
    async def get_users_with_reminders(self) -> List[Dict[str, Any]]:
        """Получение пользователей с активными напоминаниями"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self._get_users_with_reminders_sync
        )
    
    def _get_users_with_reminders_sync(self) -> List[Dict[str, Any]]:
        """Синхронное получение пользователей с напоминаниями"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, reminder_frequency FROM users 
            WHERE reminder_enabled = TRUE
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'reminder_frequency': row[1]
            })
        
        conn.close()
        return users 