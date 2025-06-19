from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from states.user_states import UserStates
from data.quiz_data import BRAIN_GAMES, BRAIN_GAME_TASKS
from data.messages import BRAIN_GAMES_INTRO
from utils.database import Database
import random
import time

class BrainGamesHandler:
    def __init__(self, database: Database):
        self.database = database
    
    async def show_brain_games_menu(self, message: types.Message, state: FSMContext):
        """Показ меню игр для мозга"""
        await state.set_state(UserStates.BRAIN_GAMES_SELECTION)
        
        keyboard_buttons = []
        for game_id, game_data in BRAIN_GAMES.items():
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"🧠 {game_data['title']}", 
                    callback_data=f"brain_game_{game_id}"
                )
            ])
        keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await message.answer(BRAIN_GAMES_INTRO, reply_markup=keyboard)
    
    async def start_brain_game(self, callback: types.CallbackQuery, state: FSMContext):
        """Начало игры для мозга"""
        game_id = callback.data.replace("brain_game_", "")
        
        if game_id not in BRAIN_GAMES:
            await callback.answer("Игра не найдена!")
            return
        
        game_data = BRAIN_GAMES[game_id]
        
        # Сохраняем данные игры в состоянии
        await state.update_data(
            game_id=game_id,
            game_data=game_data,
            current_round=0,
            score=0,
            total_rounds=5
        )
        
        await state.set_state(UserStates.BRAIN_GAME_IN_PROGRESS)
        
        # Показываем первый раунд
        await self.show_game_round(callback.message, state)
        await callback.answer()
    
    async def show_game_round(self, message: types.Message, state: FSMContext):
        """Показ текущего раунда игры"""
        data = await state.get_data()
        current_round = data['current_round']
        total_rounds = data['total_rounds']
        game_data = data['game_data']
        
        if current_round >= total_rounds:
            await self.finish_game(message, state)
            return
        
        # Генерируем задачу для текущего раунда
        task = self.generate_task(game_data['type'])
        
        # Обновляем состояние с задачей
        await state.update_data(
            current_round=current_round + 1,
            current_task=task
        )
        
        keyboard_buttons = []
        for i, option in enumerate(task['options']):
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=str(option), 
                    callback_data=f"brain_answer_{i}"
                )
            ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        round_text = f"🧠 **Раунд {current_round + 1} из {total_rounds}**\n\n{task['question']}"
        
        await message.answer(round_text, reply_markup=keyboard, parse_mode="Markdown")
    
    def generate_task(self, game_type: str) -> dict:
        """Генерация задачи для игры"""
        if game_type == "sequence":
            # Последовательности чисел
            sequence = []
            pattern = random.choice(['arithmetic', 'geometric', 'fibonacci'])
            
            if pattern == 'arithmetic':
                start = random.randint(1, 10)
                step = random.randint(2, 5)
                sequence = [start + i * step for i in range(4)]
                next_num = sequence[-1] + step
            elif pattern == 'geometric':
                start = random.randint(1, 5)
                ratio = random.randint(2, 3)
                sequence = [start * (ratio ** i) for i in range(4)]
                next_num = sequence[-1] * ratio
            else:  # fibonacci
                sequence = [1, 1, 2, 3]
                next_num = 5
            
            options = [next_num, next_num + random.randint(1, 5), next_num - random.randint(1, 3), next_num * 2]
            random.shuffle(options)
            
            return {
                'question': f"Найдите следующее число в последовательности:\n{sequence[0]}, {sequence[1]}, {sequence[2]}, {sequence[3]}, ?",
                'options': options,
                'correct': options.index(next_num)
            }
        
        elif game_type == "logic":
            # Логические задачи из quiz_data
            if game_type in BRAIN_GAME_TASKS:
                return random.choice(BRAIN_GAME_TASKS[game_type])
            else:
                # Fallback на старые данные
                tasks = [
                    {
                        'question': "Если все розы - цветы, а некоторые цветы быстро увядают, то:",
                        'options': [
                            "Все розы быстро увядают",
                            "Некоторые розы быстро увядают", 
                            "Ни одна роза не увядает",
                            "Нельзя определить"
                        ],
                        'correct': 1
                    }
                ]
                return random.choice(tasks)
        
        elif game_type == "pattern":
            # Поиск закономерности из quiz_data
            if game_type in BRAIN_GAME_TASKS:
                return random.choice(BRAIN_GAME_TASKS[game_type])
            else:
                # Fallback на старые данные
                patterns = [
                    {
                        'question': "Какая фигура должна быть следующей?\n🔴 ⚫ 🔴 ⚫ 🔴 ?",
                        'options': ["🔴", "⚫", "🔵", "🟡"],
                        'correct': 1
                    }
                ]
                return random.choice(patterns)
        
        else:
            # Fallback для неизвестных типов
            return {
                'question': "Выберите правильный ответ:",
                'options': ["Вариант A", "Вариант B", "Вариант C", "Вариант D"],
                'correct': 0
            }
    
    async def handle_game_answer(self, callback: types.CallbackQuery, state: FSMContext):
        """Обработка ответа в игре"""
        data = await state.get_data()
        current_round = data['current_round']
        total_rounds = data['total_rounds']
        score = data['score']
        current_task = data['current_task']
        
        if current_round > total_rounds:
            await callback.answer("Игра уже завершена!")
            return
        
        user_answer = int(callback.data.replace("brain_answer_", ""))
        correct_answer = current_task['correct']
        
        # Проверяем ответ
        is_correct = user_answer == correct_answer
        if is_correct:
            score += 1
        
        # Обновляем состояние
        await state.update_data(score=score)
        
        # Показываем результат
        result_text = f"✅ **Правильно!**\n\n{current_task['options'][correct_answer]}" if is_correct else f"❌ **Неправильно!**\n\nПравильный ответ: {current_task['options'][correct_answer]}"
        
        await callback.message.edit_text(result_text, parse_mode="Markdown")
        await callback.answer()
        
        # Показываем следующий раунд или завершаем игру
        if current_round < total_rounds:
            await self.show_game_round(callback.message, state)
        else:
            await self.finish_game(callback.message, state)
    
    async def finish_game(self, message: types.Message, state: FSMContext):
        """Завершение игры"""
        data = await state.get_data()
        score = data['score']
        total_rounds = data['total_rounds']
        game_id = data['game_id']
        game_data = data['game_data']
        
        # Сохраняем результат
        await self.database.save_test_result(
            user_id=message.chat.id,
            test_type=f"brain_game_{game_id}",
            score=score,
            total_questions=total_rounds
        )
        
        # Формируем результат
        percentage = (score / total_rounds) * 100
        
        if percentage >= 80:
            result_emoji = "🧠"
            result_text = "Отличная работа мозга!"
        elif percentage >= 60:
            result_emoji = "💡"
            result_text = "Хорошая логика!"
        else:
            result_emoji = "🤔"
            result_text = "Нужно тренировать мышление!"
        
        result_message = f"""
{result_emoji} **Игра завершена!**

**Игра:** {game_data['title']}
**Результат:** {score} из {total_rounds} ({percentage:.1f}%)
**Оценка:** {result_text}
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Играть еще раз", callback_data=f"brain_game_{game_id}"),
                InlineKeyboardButton(text="🧠 Другая игра", callback_data="brain_games")
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
            ]
        ])
        
        await message.answer(result_message, reply_markup=keyboard, parse_mode="Markdown")
        await state.clear() 