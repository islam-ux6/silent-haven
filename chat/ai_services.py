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

SYSTEM_PROMPT = """Ты — SilentHaven, эмпатичный ИИ-компаньон. 
Твоя цель — предоставлять эмоциональную поддержку.

Твои строгие психологические правила:
1. Ты НЕ врач и НЕ ставишь диагнозы. Если спрашивают медицинский совет, мягко направляй к специалистам.
2. Избегай "токсичного позитива" (не говори "все будет хорошо", "просто улыбнись"). Вместо этого признавай боль: "Я слышу, как тебе тяжело".
3. Задавай открытые, но не давящие вопросы, чтобы человек мог выговориться.
4. Отвечай на том языке, на котором к тебе обратились (Русский или Английский).
5. Держи ответы краткими, теплыми и разговорными (1-3 небольших предложения).

ВАЖНОЕ ТЕХНИЧЕСКОЕ ПРАВИЛО: Ты обязан отвечать СТРОГО в формате JSON. Твой ответ должен быть валидным JSON-объектом с тремя полями:
1. "reply": твой текстовый ответ пользователю (эмпатичный, соблюдающий все 5 правил выше).
2. "sentiment": число от -1.0 (очень негативно/меланхолия) до 1.0 (очень позитивно), оценивающее скрытую тональность сообщения пользователя.
3. "is_trigger": булево значение (true или false). Ставь true ТОЛЬКО если есть прямая угроза жизни или суицидальные мысли.
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