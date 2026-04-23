from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    LANGUAGE_CHOICES = [
        ('ru', 'Русский'),
        ('en', 'English'),
        ('de', 'Deutsch'),
        ('tk', 'Türkmen dili'),
    ]
    preferred_language = models.CharField(
        max_length=2, 
        choices=LANGUAGE_CHOICES, 
        default='ru',
        verbose_name="Предпочтительный язык"
    )
    
    # Поле для хранения текущего эмоционального состояния
    # Можно обновлять его после каждой сессии аналитикой
    stress_index = models.IntegerField(default=0, verbose_name="Индекс стресса")

    def __str__(self):
        return self.username