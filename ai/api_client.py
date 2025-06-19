import aiohttp
import json
import logging
import uuid
from config import GIGACHAT_AUTH_KEY

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self):
        self.auth_key = GIGACHAT_AUTH_KEY  # Это Authorization key от Сбера
        self.access_token = None
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _get_access_token(self):
        """Получение Access token для GigaChat"""
        if not self.auth_key:
            raise Exception("GigaChat Authorization key не настроен")
        
        try:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': str(uuid.uuid4()),
                'Authorization': f'Basic {self.auth_key}'
            }
            
            data = {'scope': 'GIGACHAT_API_PERS'}
            
            async with self.session.post(
                'https://ngw.devices.sberbank.ru:9443/api/v2/oauth',
                headers=headers,
                data=data,
                ssl=False  # Отключаем проверку SSL для внутренних сервисов Сбера
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.access_token = result.get('access_token')
                    return self.access_token
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка получения токена: {response.status} - {error_text}")
                    raise Exception(f"Не удалось получить Access token: {response.status}")
                    
        except Exception as e:
            logger.error(f"Ошибка при получении Access token: {e}")
            raise
    
    async def _make_gigachat_request(self, messages, max_tokens=500, temperature=0.7):
        """Выполнение запроса к GigaChat API"""
        if not self.access_token:
            await self._get_access_token()
        
        try:
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "model": "GigaChat:latest",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            async with self.session.post(
                'https://gigachat.devices.sberbank.ru/api/v1/chat/completions',
                headers=headers,
                json=data,
                ssl=False  # Отключаем проверку SSL
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                elif response.status == 401:
                    # Токен истек, получаем новый
                    await self._get_access_token()
                    # Повторяем запрос с новым токеном
                    return await self._make_gigachat_request(messages, max_tokens, temperature)
                else:
                    error_text = await response.text()
                    logger.error(f"GigaChat API error: {response.status} - {error_text}")
                    return f"❌ Ошибка API: {response.status}"
                    
        except Exception as e:
            logger.error(f"Error in GigaChat API: {e}")
            return "❌ Произошла ошибка при обработке запроса"
    
    async def get_answer(self, question: str, context: str = "") -> str:
        """Получение ответа от GigaChat"""
        if not self.auth_key:
            return "⚠️ GigaChat Authorization key не настроен. Обратитесь к администратору."
        
        try:
            # Формируем промпт с контекстом
            if context:
                system_prompt = f"""Ты помощник курса по развитию креативного мышления. 
Используй следующий контекст курса для ответов:

{context}

Отвечай кратко, по существу и дружелюбно. Если вопрос не связан с курсом, 
вежливо перенаправь на темы курса."""
            else:
                system_prompt = "Ты полезный помощник по курсу развития креативного мышления. Отвечай кратко и по существу."
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
            
            return await self._make_gigachat_request(messages, max_tokens=500, temperature=0.7)
                    
        except Exception as e:
            logger.error(f"Error in GigaChat API: {e}")
            return "❌ Произошла ошибка при обработке запроса"
    
    async def get_suggestions(self, question: str, context: str = "") -> list:
        """Получение предложений похожих вопросов"""
        if not self.auth_key:
            return []
        
        try:
            system_prompt = "Ты помощник по курсу развития креативного мышления. Предлагай релевантные вопросы."
            user_prompt = f"На основе вопроса '{question}' предложи 3 похожих вопроса по теме курса. Формат: только вопросы, каждый с новой строки."
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            result = await self._make_gigachat_request(messages, max_tokens=200, temperature=0.8)
            
            if result.startswith("❌"):
                return []
            
            return [s.strip() for s in result.split('\n') if s.strip()]
                    
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return [] 