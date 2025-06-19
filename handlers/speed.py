from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from states.user_states import UserStates
from data.quiz_data import SPEED_QUESTIONS
from data.messages import SPEED_TEST_INTRO
from utils.database import Database
import random
import time

class SpeedHandler:
    def __init__(self, database: Database):
        self.database = database
    
    async def start_speed_test(self, message: types.Message, state: FSMContext):
        """Начало теста на скорость"""
        await state.set_state(UserStates.SPEED_TEST)
        
        # Перемешиваем вопросы
        shuffled_questions = SPEED_QUESTIONS.copy()
        random.shuffle(shuffled_questions)
        
        # Сохраняем данные теста в состоянии
        await state.update_data(
            questions=shuffled_questions,
            current_question=0,
            correct_answers=0,
            total_questions=len(shuffled_questions),
            start_time=time.time()
        )
        
        await message.answer(SPEED_TEST_INTRO)
        
        # Показываем первый вопрос
        await self.show_question(message, state)
    
    async def show_question(self, message: types.Message, state: FSMContext):
        """Показ текущего вопроса"""
        data = await state.get_data()
        current_question = data['current_question']
        questions = data['questions']
        
        if current_question >= len(questions):
            await self.finish_test(message, state)
            return
        
        question_data = questions[current_question]
        
        keyboard_buttons = []
        for i, option in enumerate(question_data['options']):
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=option, 
                    callback_data=f"speed_answer_{i}"
                )
            ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        question_text = f"⚡ **Вопрос {current_question + 1} из {len(questions)}**\n\n{question_data['question']}"
        
        await message.answer(question_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def handle_answer(self, callback: types.CallbackQuery, state: FSMContext):
        """Обработка ответа на вопрос"""
        data = await state.get_data()
        current_question = data['current_question']
        questions = data['questions']
        correct_answers = data['correct_answers']
        
        if current_question >= len(questions):
            await callback.answer("Тест уже завершен!")
            return
        
        question_data = questions[current_question]
        user_answer = int(callback.data.replace("speed_answer_", ""))
        correct_answer = question_data['correct']
        
        # Проверяем ответ
        is_correct = user_answer == correct_answer
        if is_correct:
            correct_answers += 1
        
        # Обновляем состояние
        await state.update_data(
            current_question=current_question + 1,
            correct_answers=correct_answers
        )
        
        # Показываем результат
        result_text = f"✅ **Правильно!**\n\n{question_data['explanation']}" if is_correct else f"❌ **Неправильно!**\n\nПравильный ответ: {question_data['options'][correct_answer]}\n\n{question_data['explanation']}"
        
        await callback.message.edit_text(result_text, parse_mode="Markdown")
        await callback.answer()
        
        # Показываем следующий вопрос или завершаем тест
        if current_question + 1 < len(questions):
            await self.show_question(callback.message, state)
        else:
            await self.finish_test(callback.message, state)
    
    async def finish_test(self, message: types.Message, state: FSMContext):
        """Завершение теста"""
        data = await state.get_data()
        correct_answers = data['correct_answers']
        total_questions = data['total_questions']
        start_time = data['start_time']
        
        completion_time = time.time() - start_time
        
        # Сохраняем результат
        await self.database.save_test_result(
            user_id=message.chat.id,
            test_type="speed",
            score=correct_answers,
            total_questions=total_questions,
            completion_time=completion_time
        )
        
        # Формируем результат
        percentage = (correct_answers / total_questions) * 100
        avg_time = completion_time / total_questions
        
        if percentage >= 80 and avg_time < 10:
            result_emoji = "🚀"
            result_text = "Отличная скорость и точность!"
        elif percentage >= 60:
            result_emoji = "⚡"
            result_text = "Хорошая скорость!"
        else:
            result_emoji = "🐌"
            result_text = "Нужно тренировать скорость!"
        
        result_message = f"""
{result_emoji} **Тест на скорость завершен!**

**Результат:** {correct_answers} из {total_questions} ({percentage:.1f}%)
**Время:** {completion_time:.1f} сек
**Среднее время на вопрос:** {avg_time:.1f} сек
**Оценка:** {result_text}
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Пройти еще раз", callback_data="speed"),
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
            ]
        ])
        
        await message.answer(result_message, reply_markup=keyboard, parse_mode="Markdown")
        await state.clear() 