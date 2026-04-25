from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_interface, name='chat_interface'),
    path('send/', views.send_message, name='send_message'),
    path('chat/<int:session_id>', views.chat_interface, name="chat_with_id"),
    path("new_chat/", views.start_new_chat, name="new_chat"),
    path('chat/<int:session_id>/delete/', views.delete_chat, name='delete_chat'),
    path('chat/<int:session_id>/rename/', views.rename_chat, name='rename_chat'),
]
