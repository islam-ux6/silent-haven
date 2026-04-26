import os
import json
from groq import Groq
from dotenv import load_dotenv

# Загружаем секреты из файла .env
load_dotenv()

# Достаем ключ безопасно
API_KEY = os.getenv("GROQ_API_KEY")

# Инициализируем клиента Groq
if API_KEY:
    client = Groq(api_key=API_KEY)
else:
    client = None

SYSTEM_PROMPT = """Ты — SilentHaven, эмпатичный, спокойный и искренне заинтересованный ИИ-компаньон. 
Твоя цель — бережно помогать пользователю разобраться в своих чувствах.

Твои строгие психологические правила:
1. НЕ отправляй к специалистам при жалобах на грусть, усталость или выгорание. Делай это ТОЛЬКО при угрозе жизни.
2. Проявляй теплое любопытство. Задавай открытые вопросы.
3. Никакого "токсичного позитива". Валидируй боль.
4. Помогай нащупать опору.
5. Отвечай кратко (2-4 предложения).

ВАЖНОЕ ТЕХНИЧЕСКОЕ ПРАВИЛО: Ты обязан отвечать СТРОГО в формате JSON:
1. "reply": текстовый ответ пользователю.
2. "emotions": объект с оценкой от 0.0 до 1.0. Строго 4 ключа: "anxiety" (тревога), "sadness" (грусть), "anger" (гнев), "apathy" (апатия).
3. "primary_emotion": главная эмоция (одно слово на английском: anxiety, sadness, anger, apathy или neutral).
4. "stress_factors": массив строк, короткие причины стресса (например: ["учеба", "дедлайн"]). Если их нет — пустой массив [].
5. "is_trigger": true/false (угроза жизни).
6. "chat_title": короткое название темы диалога (2-3 слова).
"""


def get_ai_response_and_analysis(messages_history):
    """
    Отправляет историю в Groq и возвращает разобранный JSON с ответом и аналитикой.
    """

    # 2. Проверка ключа
    if not client:
        return {"reply": "API ключ не настроеню", "sentiment": 0, "is_trigger":False}
    
    try:
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages_history

        # Отправляем запрос на серверы Groq
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Быстрая и умная модель от Meta, доступная в Groq
            messages=api_messages,
            temperature=0.7,
            max_tokens=1024, 
            response_format={"type": "json_object"}
        )

        raw_json_string = completion.choices[0].message.content

        ai_data = json.loads(raw_json_string)
        return ai_data
        
    except Exception as e:
        print(f"Ошибка API Groq: {e}") 
        return {
            "reply": "Извини, небольшая заминка с сетью. Попробуем еще раз?",
            "sentiment": 0,
            "is_trigger": False
        }