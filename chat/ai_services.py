import os
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем секреты из файла .env
load_dotenv()

# Достаем ключ безопасно
API_KEY = os.getenv("OPENROUTER_API_KEY")

# Инициализируем клиента, направляя его на серверы OpenRouter
if API_KEY:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
    )
else:
    client = None
    print("ВНИМАНИЕ: API ключ не найден в файле .env!")

# Тот самый "мозг" и характер бота
SYSTEM_PROMPT = """Ты — SilentHaven, эмпатичный ИИ-компаньон. 
Твоя цель — предоставлять эмоциональную поддержку, использовать активное слушание и валидировать чувства пользователя, страдающего от одиночества, выгорания или стресса.

Твои строгие правила:
1. Ты НЕ врач и НЕ ставишь диагнозы. Если спрашивают медицинский совет, мягко направляй к специалистам.
2. Избегай "токсичного позитива" (не говори "все будет хорошо", "просто улыбнись"). Вместо этого признавай боль: "Я слышу, как тебе тяжело".
3. Задавай открытые, но не давящие вопросы, чтобы человек мог выговориться.
4. Отвечай на том языке, на котором к тебе обратились (Русский или Английский).
5. Держи ответы краткими, теплыми и разговорными (1-3 небольших предложения).
"""

def analyze_sentiment_and_triggers(text):
    """
    NLP-функция проверки на красные флаги.
    """
    text_lower = text.lower()
    
    danger_words = ['убить', 'смысл', 'закончить', 'не хочу жить', 'суицид', 'kill', 'suicide', 'end it', 'hopeless']
    is_trigger = any(word in text_lower for word in danger_words)
    
    negative_words = ['грустно', 'одиноко', 'плохо', 'тоска', 'боль', 'sad', 'lonely', 'pain', 'depressed']
    sentiment = -0.5 if any(word in text_lower for word in negative_words) else 0.1
    
    return is_trigger, sentiment

def get_ai_response(user_text, is_trigger):
    """
    Функция обращения к LLM через OpenRouter.
    """
    # 1. Жесткий перехват
    if is_trigger:
        return ("Я вижу, что тебе сейчас невероятно тяжело и небезопасно. Пожалуйста, знай, что твоя жизнь важна. "
                "Я всего лишь ИИ, но я хочу, чтобы ты получил реальную поддержку. Пожалуйста, обратись к специалистам или близким прямо сейчас.")
    
    # 2. Проверка ключа
    if not client:
        return "Система настроена! Но чтобы я мог отвечать осмысленно, разработчику нужно добавить OPENROUTER_API_KEY в файл .env."

    try:
        # Отправляем запрос
        completion = client.chat.completions.create(
        model="meta-llama/llama-3.1-8b-instruct:free", # Обновленная версия
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0.7,
    )
        
        # Возвращаем сгенерированный текст
        return completion.choices[0].message.content
        
    except Exception as e:
        print(f"Ошибка API OpenRouter: {e}") 
        return "Извини, мне сейчас немного трудно сосредоточиться (ошибка соединения). Давай попробуем еще раз через минуту?"