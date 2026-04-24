from django.shortcuts import render
from chat.models import Message

def dashboard(request):
    """
    Собирает данные о тональности сообщений для графика.
    """
    # Берем все сообщения от пользователя (сортируем по времени)
    user_messages = Message.objects.filter(sender='user').order_by('timestamp')
    
    # Подготавливаем списки для графика
    timestamps = []
    sentiments = []
    
    for msg in user_messages:
        # Форматируем время для красоты (например: "14:30")
        timestamps.append(msg.timestamp.strftime("%H:%M"))
        # Добавляем оценку настроения (если она есть, иначе 0)
        sentiments.append(msg.sentiment_value if msg.sentiment_value else 0)
    
    context = {
        'timestamps': timestamps,
        'sentiments': sentiments,
    }
    
    return render(request, 'analytics/dashboard.html', context)