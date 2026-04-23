from django.db import models
from django.conf import settings

class DailyMoodLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    
    # Средние показатели за день
    avg_sentiment = models.FloatField(verbose_name="Средняя тональность")
    dominant_emotion = models.CharField(max_length=100, verbose_name="Доминирующая эмоция")
    
    # Например: "одиночество", "меланхолия", "спокойствие"
    emotional_tags = models.JSONField(default=list, verbose_name="Эмоциональные теги")

    class Meta:
        unique_together = ('user', 'date')