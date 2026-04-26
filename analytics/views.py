import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.db.models.functions import TruncDate
from chat.models import Message

@login_required(login_url='/login/')
def dashboard(request):
    # Берем только сообщения пользователя, чтобы анализировать его состояние
    user_messages = Message.objects.filter(sender='user', session__user=request.user)

    # --- 1. ДАННЫЕ ДЛЯ РАДАР-ГРАФИКА (СРЕДНЕЕ) ---
    averages = user_messages.aggregate(
        avg_anxiety=Avg('anxiety'),
        avg_sadness=Avg('sadness'),
        avg_anger=Avg('anger'),
        avg_apathy=Avg('apathy')
    )

    radar_data = [
        round(averages['avg_anxiety'] or 0, 2),
        round(averages['avg_sadness'] or 0, 2),
        round(averages['avg_anger'] or 0, 2),
        round(averages['avg_apathy'] or 0, 2)
    ]

    # --- 2. ДАННЫЕ ДЛЯ ТЕГОВ (ФАКТОРЫ СТРЕССА) ---
    all_factors = []
    for msg in user_messages:
        if msg.stress_factors:
            factors = [f.strip().lower() for f in msg.stress_factors.split(',')]
            all_factors.extend(factors)

    factor_counts = {}
    for f in all_factors:
        if f:
            factor_counts[f] = factor_counts.get(f, 0) + 1

    top_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)[:7]

    # --- 3. ДАННЫЕ ДЛЯ ЛИНЕЙНОГО ГРАФИКА (ДИНАМИКА) ---
    # Группируем сообщения по дням и считаем среднее для каждого дня
    daily_stats_qs = user_messages.annotate(date=TruncDate('timestamp')) \
        .values('date') \
        .annotate(
            anxiety=Avg('anxiety'),
            sadness=Avg('sadness'),
            anger=Avg('anger'),
            apathy=Avg('apathy')
        ).order_by('-date')[:14] 

    # Шаг 2: Превращаем в список и переворачиваем обратно (хронологический порядок)
    daily_stats = list(daily_stats_qs)[::-1]

    # Формируем списки для JavaScript
    dates = [stat['date'].strftime('%d.%m') for stat in daily_stats]
    trend_anxiety = [round(stat['anxiety'] or 0, 2) for stat in daily_stats]
    trend_sadness = [round(stat['sadness'] or 0, 2) for stat in daily_stats]
    trend_anger = [round(stat['anger'] or 0, 2) for stat in daily_stats]
    trend_apathy = [round(stat['apathy'] or 0, 2) for stat in daily_stats]

    context = {
        'radar_data': radar_data,
        'top_factors': top_factors,
        'dates_json': json.dumps(dates),
        'anxiety_json': json.dumps(trend_anxiety),
        'sadness_json': json.dumps(trend_sadness),
        'anger_json': json.dumps(trend_anger),
        'apathy_json': json.dumps(trend_apathy),
    }
    
    return render(request, 'analytics/dashboard.html', context)