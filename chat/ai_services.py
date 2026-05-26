import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if API_KEY:
    client = Groq(api_key=API_KEY)
else:
    client = None

def get_ai_response_and_analysis(messages_history, user_context=""):
    SYSTEM_PROMPT = f"""You are SilentHaven, an empathetic AI companion. Reply STRICTLY in English.

    {user_context}

    Your rules:
    1. Be a friend, not a doctor. Use a soft, conversational tone.
    2. If the user writes vaguely, use data from [SECRET CONTEXT] to ask a guiding question.
    3. CRITICAL FOR JSON: 
       - Normal complaints ("tired", "problems") = anxiety from 0.3 to 0.6.
       - Acute panic ("choking", "scared", "panic attack") = anxiety from 0.85 to 1.0.
       NEVER set anxiety above 0.8 for ordinary life difficulties.

    JSON FORMAT:
    1. "reply": empathetic response in English.
    2. "emotions": {{"anxiety": 0.0, "sadness": 0.0, "anger": 0.0, "apathy": 0.0}}.
    3. "primary_emotion": current main emotion.
    4. "stress_factors": extracted triggers in English (e.g., ["work", "exam"]).
    5. "is_trigger": true ONLY for life threats.
    6. "chat_title": short title (2-3 words in English).
    """

    if not client:
        return {"reply": "API key is not configured.", "emotions": {"anxiety": 0}, "is_trigger": False}
    
    try:
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages_history

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=api_messages,
            temperature=0.7,
            max_tokens=1024, 
            response_format={"type": "json_object"}
        )

        raw_json_string = completion.choices[0].message.content
        ai_data = json.loads(raw_json_string)
        return ai_data
        
    except Exception as e:
        print(f"Groq API Error: {e}") 
        return {
            "reply": "Sorry, there's a slight network issue. Should we try again?",
            "emotions": {"anxiety": 0},
            "is_trigger": False
        }