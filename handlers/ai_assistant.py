from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from states.user_states import UserStates
from data.messages import AI_WELCOME_MESSAGE, AI_THINKING_MESSAGE, AI_ERROR_MESSAGE
from ai.api_client import AIClient
from ai.context_manager import ContextManager
from utils.database import Database

class AIAssistantHandler:
    def __init__(self, database: Database):
        self.database = database
        self.context_manager = ContextManager()
        
    async def start_ai_chat(self, message: types.Message, state: FSMContext):
        """Начало чата с ИИ"""
        await state.set_state(UserStates.AI_CHAT)
        await message.answer(AI_WELCOME_MESSAGE)
        
    async def handle_ai_question(self, message: types.Message, state: FSMContext):
        """Обработка вопроса к ИИ"""
        question = message.text
        
        # Показываем индикатор загрузки
        loading_msg = await message.answer(AI_THINKING_MESSAGE)
        
        try:
            async with AIClient() as ai_client:
                # Получаем контекст
                context = self.context_manager.get_context_for_question(question)
                
                # Получаем ответ от ИИ
                answer = await ai_client.get_answer(question, context)
                
                # Получаем предложения похожих вопросов
                suggestions = await ai_client.get_suggestions(question, context)
                
                # Удаляем сообщение о загрузке
                await loading_msg.delete()
                
                # Сохраняем взаимодействие
                await self.database.save_ai_interaction(
                    user_id=message.from_user.id,
                    question=question,
                    answer=answer
                )
                
                # Формируем ответ с кнопками
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="👍 Полезно", callback_data="ai_like"),
                        InlineKeyboardButton(text="👎 Не полезно", callback_data="ai_dislike")
                    ],
                    [
                        InlineKeyboardButton(text="🔄 Задать еще вопрос", callback_data="ai_another")
                    ]
                ])
                
                response = f"🤖 **Ответ:**\n\n{answer}\n\n"
                
                if suggestions:
                    response += "💡 **Похожие вопросы:**\n"
                    for i, suggestion in enumerate(suggestions[:3], 1):
                        response += f"{i}. {suggestion}\n"
                
                response += "\nОцени ответ:"
                
                await message.answer(response, reply_markup=keyboard, parse_mode="Markdown")
                
                # Сохраняем вопрос и ответ в состоянии
                await state.update_data(last_question=question, last_answer=answer)
                await state.set_state(UserStates.AI_FEEDBACK)
                
        except Exception as e:
            await loading_msg.delete()
            await message.answer(AI_ERROR_MESSAGE)
            await state.set_state(UserStates.AI_CHAT)
    
    async def handle_ai_feedback(self, callback: types.CallbackQuery, state: FSMContext):
        """Обработка обратной связи по ответу ИИ"""
        feedback_type = callback.data
        
        if feedback_type == "ai_like":
            feedback_value = 1
            await callback.answer("👍 Спасибо! Рад, что ответ был полезен!")
        elif feedback_type == "ai_dislike":
            feedback_value = 0
            await callback.answer("👎 Спасибо за обратную связь! Буду стараться лучше.")
        elif feedback_type == "ai_another":
            await callback.answer("🔄 Задавайте следующий вопрос!")
            await state.set_state(UserStates.AI_CHAT)
            return
        
        # Сохраняем обратную связь
        data = await state.get_data()
        if 'last_question' in data and 'last_answer' in data:
            await self.database.save_ai_interaction(
                user_id=callback.from_user.id,
                question=data['last_question'],
                answer=data['last_answer'],
                feedback=feedback_value
            )
        
        # Возвращаемся в режим чата
        await state.set_state(UserStates.AI_CHAT) 