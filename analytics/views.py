import datetime
import json
import math
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from chat.models import Message

@login_required(login_url='/login/')
def dashboard(request):
    user_messages = Message.objects.filter(sender='user', session__user=request.user)

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

    daily_stats_qs = user_messages.annotate(date=TruncDate('timestamp')) \
        .values('date') \
        .annotate(
            anxiety=Avg('anxiety'),
            sadness=Avg('sadness'),
            anger=Avg('anger'),
            apathy=Avg('apathy')
        ).order_by('-date')[:14] 

    daily_stats = list(daily_stats_qs)[::-1]

    dates = [stat['date'].strftime('%d.%m') for stat in daily_stats]
    trend_anxiety = [round(stat['anxiety'] or 0, 2) for stat in daily_stats]
    trend_sadness = [round(stat['sadness'] or 0, 2) for stat in daily_stats]
    trend_anger = [round(stat['anger'] or 0, 2) for stat in daily_stats]
    trend_apathy = [round(stat['apathy'] or 0, 2) for stat in daily_stats]

    volatility_index = 0.0
    volatility_status = "Not enough data"
    volatility_color = "secondary"

    if len(trend_anxiety) > 1:
        n = len(trend_anxiety)
        mu = sum(trend_anxiety) / n
        variance = sum((x - mu) ** 2 for x in trend_anxiety) / n
        sigma = math.sqrt(variance)
        volatility_index = round(sigma, 2)

        if volatility_index >= 0.25:
            volatility_status = "High Volatility (Sharp Anxiety Spikes)"
            volatility_color = "danger"
        elif volatility_index >= 0.15:
            volatility_status = "Moderate Instability"
            volatility_color = "warning"
        else:
            volatility_status = "Emotional Stability"
            volatility_color = "success"

    weekday_anxiety = {i: [] for i in range(7)}
    
    for msg in user_messages:
        if msg.anxiety is not None:
            weekday = msg.timestamp.weekday()
            weekday_anxiety[weekday].append(msg.anxiety)

    weekday_averages = {}
    for day, values in weekday_anxiety.items():
        weekday_averages[day] = sum(values) / len(values) if values else 0.0

    tomorrow = timezone.now().date() + datetime.timedelta(days=1)
    tomorrow_weekday = tomorrow.weekday()
    
    tomorrow_expected = weekday_averages.get(tomorrow_weekday, 0.0)
    overall_avg = averages['avg_anxiety'] or 0.0

    days_en = ["Mondays", "Tuesdays", "Wednesdays", "Thursdays", "Fridays", "Saturdays", "Sundays"]
    
    if tomorrow_expected > (overall_avg * 1.2) and tomorrow_expected > 0.4:
        forecast_status = f"Stress Spike Expected (Pattern for {days_en[tomorrow_weekday]})"
        forecast_message = "Our AI analysis shows that your anxiety level is usually higher than average on this day of the week. We recommend planning some rest time in advance and avoiding overworking."
        forecast_color = "warning"
        forecast_icon = "⚠️"
    else:
        forecast_status = "Emotional Background is Stable"
        forecast_message = "Historical data shows that tomorrow is usually a calm day for you. Keep it up!"
        forecast_color = "info"
        forecast_icon = "🔮"

    context = {
        'radar_data': radar_data,
        'top_factors': top_factors,
        'dates_json': json.dumps(dates),
        'anxiety_json': json.dumps(trend_anxiety),
        'sadness_json': json.dumps(trend_sadness),
        'anger_json': json.dumps(trend_anger),
        'apathy_json': json.dumps(trend_apathy),
        'volatility_index': volatility_index,
        'volatility_status': volatility_status,
        'volatility_color': volatility_color,
        'forecast_status': forecast_status,
        'forecast_message': forecast_message,
        'forecast_color': forecast_color,
        'forecast_icon': forecast_icon,
    }
    return render(request, 'analytics/dashboard.html', context)