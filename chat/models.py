from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Поле для краткого резюме сессии, которое может генерировать ИИ
    summary = models.TextField(blank=True, verbose_name="Краткое содержание сессии")

    class Meta:
        verbose_name = "Сессия чата"
        verbose_name_plural = "Сессии чата"

class Message(models.Model):
    SENDER_CHOICES = [('user', 'Пользователь'), ('ai', 'ИИ-компаньон')]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=4, choices=SENDER_CHOICES)
    text = models.TextField(verbose_name="Текст сообщения")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Поля для мгновенного NLP-анализа
    is_trigger_alert = models.BooleanField(default=False, verbose_name="Критический маркер")
    sentiment_value = models.FloatField(null=True, blank=True, verbose_name="Тональность (-1 до 1)")

class EmergencyResource(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название службы")
    phone = models.CharField(max_length=20, verbose_name="Номер телефона")
    country_code = models.CharField(max_length=10, verbose_name="Код страны (напр. TM, RU, DE)")
    
    def __str__(self):
        return f"{self.title} ({self.country_code})"