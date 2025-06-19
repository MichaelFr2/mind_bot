from ai.ai_curator import COURSE_CONTEXT

class ContextManager:
    def __init__(self):
        self.context_data = COURSE_CONTEXT
    
    def get_context_for_question(self, question: str) -> str:
        """Получение релевантного контекста для вопроса"""
        # Пока возвращаем весь контекст
        # В будущем можно добавить логику выбора релевантных частей
        return self.context_data
    
    def get_full_context(self) -> str:
        """Получение полного контекста курса"""
        return self.context_data 