from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from states.user_states import UserStates
from data.quiz_data import QUIZ_MODULES
from data.messages import QUIZ_SELECTION_MESSAGE
from utils.database import Database
import random

class QuizHandler:
    def __init__(self, database: Database):
        self.database = database
    
    async def show_quiz_selection(self, message: types.Message, state: FSMContext):
        """Показ выбора модуля для квиза"""
        await state.set_state(UserStates.QUIZ_SELECTION)
        
        keyboard_buttons = []
        for module_id, module_data in QUIZ_MODULES.items():
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"📚 {module_data['title']}", 
                    callback_data=f"quiz_module_{module_id}"
                )
            ])
        keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await message.answer(QUIZ_SELECTION_MESSAGE, reply_markup=keyboard)
    
    async def start_quiz(self, callback: types.CallbackQuery, state: FSMContext):
        """Начало квиза по выбранному модулю"""
        module_id = callback.data.replace("quiz_module_", "")
        
        if module_id not in QUIZ_MODULES:
            await callback.answer("Модуль не найден!")
            return
        
        module_data = QUIZ_MODULES[module_id]
        questions = module_data['questions']
        
        # Перемешиваем вопросы
        shuffled_questions = questions.copy()
        random.shuffle(shuffled_questions)
        
        # Сохраняем данные квиза в состоянии
        await state.update_data(
            quiz_module=module_id,
            questions=shuffled_questions,
            current_question=0,
            correct_answers=0,
            total_questions=len(shuffled_questions)
        )
        
        await state.set_state(UserStates.QUIZ_IN_PROGRESS)
        
        # Показываем первый вопрос
        await self.show_question(callback.message, state)
        await callback.answer()
    
    async def show_question(self, message: types.Message, state: FSMContext):
        """Показ текущего вопроса"""
        data = await state.get_data()
        current_question = data['current_question']
        questions = data['questions']
        
        if current_question >= len(questions):
            await self.finish_quiz(message, state)
            return
        
        question_data = questions[current_question]
        
        keyboard_buttons = []
        for i, option in enumerate(question_data['options']):
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{chr(97 + i)}) {option}", 
                    callback_data=f"quiz_answer_{i}"
                )
            ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        question_text = f"📚 **Вопрос {current_question + 1} из {len(questions)}**\n\n{question_data['question']}"
        
        await message.answer(question_text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def handle_answer(self, callback: types.CallbackQuery, state: FSMContext):
        """Обработка ответа на вопрос"""
        data = await state.get_data()
        current_question = data['current_question']
        questions = data['questions']
        correct_answers = data['correct_answers']
        
        if current_question >= len(questions):
            await callback.answer("Квиз уже завершен!")
            return
        
        question_data = questions[current_question]
        user_answer = int(callback.data.replace("quiz_answer_", ""))
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
        
        # Показываем следующий вопрос или завершаем квиз
        if current_question + 1 < len(questions):
            await self.show_question(callback.message, state)
        else:
            await self.finish_quiz(callback.message, state)
    
    async def finish_quiz(self, message: types.Message, state: FSMContext):
        """Завершение квиза"""
        data = await state.get_data()
        correct_answers = data['correct_answers']
        total_questions = data['total_questions']
        module_id = data['quiz_module']
        
        # Сохраняем результат
        await self.database.save_test_result(
            user_id=message.chat.id,
            test_type=f"quiz_{module_id}",
            score=correct_answers,
            total_questions=total_questions
        )
        
        # Формируем результат
        percentage = (correct_answers / total_questions) * 100
        
        if percentage >= 80:
            result_emoji = "🎉"
            result_text = "Отличный результат!"
        elif percentage >= 60:
            result_emoji = "👍"
            result_text = "Хороший результат!"
        else:
            result_emoji = "📚"
            result_text = "Есть куда расти!"
        
        result_message = f"""
{result_emoji} **Квиз завершен!**

**Результат:** {correct_answers} из {total_questions} ({percentage:.1f}%)
**Оценка:** {result_text}

Модуль: {QUIZ_MODULES[module_id]['title']}
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Пройти еще раз", callback_data=f"quiz_module_{module_id}"),
                InlineKeyboardButton(text="📚 Другой модуль", callback_data="quiz")
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
            ]
        ])
        
        await message.answer(result_message, reply_markup=keyboard, parse_mode="Markdown")
        await state.clear() 