from django.contrib import admin
from .models import ChatSession, Message

# Настраиваем отображение сессий
@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    # Какие колонки показывать в списке
    list_display = ('id', 'user', 'created_at')
    # По каким полям можно искать (ищем по логину пользователя)
    search_fields = ('user__username',)
    # По каким полям можно фильтровать сбоку
    list_filter = ('created_at',)

# Настраиваем отображение сообщений
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    # Выводим все важные метрики прямо в таблицу
    list_display = ('id', 'session_info', 'sender', 'short_text', 'sentiment_value', 'is_trigger_alert', 'timestamp')
    
    # Добавляем боковую панель с фильтрами (очень удобно искать все сообщения с триггерами!)
    list_filter = ('is_trigger_alert', 'sender', 'timestamp')
    
    # Добавляем строку поиска по тексту сообщения
    search_fields = ('text',)
    
    # Сортируем так, чтобы новые сообщения всегда были сверху
    ordering = ('-timestamp',)

    # Кастомный метод, чтобы длинные сообщения не ломали таблицу
    def short_text(self, obj):
        if len(obj.text) > 50:
            return obj.text[:50] + '...'
        return obj.text
    short_text.short_description = 'Текст сообщения'

    # Кастомный метод для красивого отображения ID сессии и логина
    def session_info(self, obj):
        return f"Сессия {obj.session.id} ({obj.session.user.username})"
    session_info.short_description = 'Сессия'