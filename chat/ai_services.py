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

def get_ai_response_and_analysis(messages_history, user_context=""):
    """
    Отправляет историю в Groq и возвращает разобранный JSON с ответом и аналитикой.
    """

    # ИСПРАВЛЕНИЕ: Жесткие правила для математики в JSON
    SYSTEM_PROMPT = f"""Ты — SilentHaven, эмпатичный ИИ-компаньон. Отвечай СТРОГО на русском языке.

    {user_context}

    Твои правила:
    1. Будь другом, а не врачом. Используй мягкий, разговорный стиль.
    2. Если пользователь пишет размыто, используй данные из [СЕКРЕТНЫЙ КОНТЕКСТ], чтобы задать наводящий вопрос (например, про работу или учебу).
    3. КРИТИЧЕСКИ ВАЖНО ДЛЯ JSON: 
       - Обычные жалобы ("устал", "проблемы", "накатило") = anxiety от 0.3 до 0.6.
       - Острая паника ("задыхаюсь", "страшно", "паническая атака") = anxiety от 0.85 до 1.0.
       НИКОГДА не ставь anxiety выше 0.8 для обычных жизненных трудностей.

    ФОРМАТ JSON:
    1. "reply": эмпатичный ответ.
    2. "emotions": {{"anxiety": 0.0, "sadness": 0.0, "anger": 0.0, "apathy": 0.0}}.
    3. "primary_emotion": актуальная эмоция.
    4. "stress_factors": извлеченные триггеры.
    5. "is_trigger": true только при угрозе жизни.
    6. "chat_title": короткая тема.
    """

    if not client:
        return {"reply": "API ключ не настроен", "emotions": {"anxiety": 0}, "is_trigger":False}
    
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
            "emotions": {"anxiety": 0},
            "is_trigger": False
        }