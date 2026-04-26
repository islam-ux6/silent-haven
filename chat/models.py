from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Новый чат")
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10) 
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Старое поле (оставляем для совместимости)
    sentiment_value = models.FloatField(null=True, blank=True)
    is_trigger_alert = models.BooleanField(default=False)

    # --- НОВЫЕ АНАЛИТИЧЕСКИЕ ПОЛЯ ---
    anxiety = models.FloatField(default=0.0) # Тревога
    sadness = models.FloatField(default=0.0) # Грусть/Уныние
    anger = models.FloatField(default=0.0)   # Гнев/Раздражение
    apathy = models.FloatField(default=0.0)  # Апатия/Выгорание
    primary_emotion = models.CharField(max_length=50, default='neutral') # Главная эмоция
    stress_factors = models.CharField(max_length=255, blank=True, null=True) # Источники стресса через запятую