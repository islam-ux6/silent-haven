from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Какие колонки показывать в списке пользователей
    list_display = ('username', 'email', 'is_staff', 'date_joined')
    # По каким полям искать
    search_fields = ('username', 'email')
    # Боковой фильтр
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    # Группировка полей в самой карточке пользователя
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio',)}), # Если вы добавляли поле bio в модель
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('bio',)}),
    )