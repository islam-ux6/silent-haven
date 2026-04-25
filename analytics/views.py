from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from chat.models import Message

@login_required(login_url='/login/')
def dashboard(request):
    """
    Собирает данные о тональности сообщений для графика.
    """
    
    user_messages = Message.objects.filter(
        sender='user',
        session__user=request.user
    ).order_by('timestamp')
    
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