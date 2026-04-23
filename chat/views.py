from django.shortcuts import render
from django.http import JsonResponse
from .models import ChatSession, Message
from .ai_services import analyze_sentiment_and_triggers, get_ai_response

def chat_interface(request):
    """
    Эта функция просто отображает саму HTML-страницу чата.
    """
    return render(request, 'chat/index.html')

def send_message(request):
    """
    Эта функция принимает сообщение пользователя через AJAX (без перезагрузки страницы),
    обрабатывает его и возвращает ответ ИИ.
    """
    if request.method == "POST":
        user_text = request.POST.get('message')
        
        # Для MVP берем первую попавшуюся сессию пользователя или создаем новую
        # (В идеале здесь нужно проверять request.user, но пока упростим)
        session, created = ChatSession.objects.get_or_create(user=request.user)
        
        # 1. Анализируем текст
        is_trigger, sentiment = analyze_sentiment_and_triggers(user_text)
        
        # 2. Сохраняем сообщение пользователя в БД
        Message.objects.create(
            session=session,
            sender='user',
            text=user_text,
            is_trigger_alert=is_trigger,
            sentiment_value=sentiment
        )
        
        # 3. Получаем ответ от ИИ
        ai_text = get_ai_response(user_text, is_trigger)
        
        # 4. Сохраняем ответ ИИ в БД
        Message.objects.create(
            session=session,
            sender='ai',
            text=ai_text
        )
        
        # 5. Отдаем ответ обратно на веб-страницу
        return JsonResponse({
            'response': ai_text,
            'is_trigger': is_trigger
        })