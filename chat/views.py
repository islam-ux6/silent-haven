from django.shortcuts import render
from django.http import JsonResponse
from .models import ChatSession, Message
from .ai_services import get_ai_response_and_analysis

def chat_interface(request):
    """
    Эта функция просто отображает саму HTML-страницу чата.
    """
    return render(request, 'chat/index.html')

def send_message(request):
    if request.method == "POST":
        user_text = request.POST.get('message')
        session, created = ChatSession.objects.get_or_create(user=request.user)
        
        user_msg = Message.objects.create(
            session=session,
            sender="user",
            text=user_text
        )

        last_messages = Message.objects.filter(session=session).order_by('-timestamp')[:6]
        history = []
        for msg in reversed(last_messages):
            role = 'user' if msg.sender == 'user' else 'assistant'
            history.append({"role": role, "content": msg.text})

        ai_data = get_ai_response_and_analysis(history)

        reply_text = ai_data.get('reply', 'Извини, я задумался.')
        sentiment = ai_data.get('sentiment', 0.1)
        is_trigger = ai_data.get('is_trigger', False)

        user_msg.sentiment_value = sentiment
        user_msg.is_trigger_alert = is_trigger
        user_msg.save()

        if is_trigger:
            reply_text = ("Я вижу, что тебе сейчас невероятно тяжело и небезопасно. "
                          "Пожалуйста, знай, что твоя жизнь важна. Обратись к специалистам прямо сейчас.")
        
        Message.objects.create(
            session=session,
            sender='ai',
            text=reply_text
        )

        return JsonResponse({
            'response': reply_text,
            'is_trigger': is_trigger
        })