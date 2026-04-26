from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
import json
from .models import ChatSession, Message
from .ai_services import get_ai_response_and_analysis
from .forms import CustomUserCreationForm

def chat_interface(request):
    """
    Эта функция просто отображает саму HTML-страницу чата.
    """
    return render(request, 'chat/index.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat_interface')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required(login_url='/login/')
def chat_interface(request, session_id=None):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    
    if session_id:
        current_session = ChatSession.objects.get(id=session_id, user=request.user)
    else:
        current_session = sessions.first()
        if not current_session:
            current_session = ChatSession.objects.create(user=request.user)
    
    messages = Message.objects.filter(session=current_session).order_by('timestamp')
    
    return render(request, 'chat/index.html', {
        'sessions': sessions,
        'current_session': current_session,
        'messages': messages
    })

@login_required
def start_new_chat(request):
    new_session = ChatSession.objects.create(user=request.user)
    return redirect('chat_with_id', session_id=new_session.id)

@login_required(login_url='/login/')
def send_message(request):
    if request.method == "POST":
        user_text = request.POST.get('message')
        session_id = request.POST.get('session_id')
        
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Сессия не найдена'}, status=400)
        
        user_msg = Message.objects.create(session=session, sender='user', text=user_text)
        
        last_messages = Message.objects.filter(session=session).order_by('-timestamp')[:6]
        history = [{"role": 'user' if m.sender == 'user' else 'assistant', "content": m.text} for m in reversed(last_messages)]

        recent_global = Message.objects.filter(session__user=request.user, sender='user').order_by('-timestamp')[:20]

        user_context = ""
        if recent_global:
            avg_anx = sum(m.anxiety for m in recent_global) / len(recent_global)

            recent_factors = []
            for m in recent_global:
                if m.stress_factors:
                    recent_factors.extend([f.strip() for f in m.stress_factors.split(',') if f.strip()])
            
            top_recent_factors = list(set(recent_factors))[:3]

            # ИСПРАВЛЕНИЕ: Даем более четкую инструкцию, чтобы избежать якорения
            user_context = f"""
            [СЕКРЕТНЫЙ КОНТЕКСТ ДЛЯ ИИ]: 
            В последнее время средний уровень тревоги пользователя: {avg_anx:.2f} из 1.0. 
            Недавние источники стресса: {', '.join(top_recent_factors)}. 
            ИНСТРУКЦИЯ: Используй это только для ведения диалога. Оценивай JSON эмоции (anxiety) СТРОГО по последнему сообщению, не копируй прошлую среднюю тревогу!
            """
            
        # ИСПРАВЛЕНИЕ: Убрали дублирующийся запрос без контекста
        ai_data = get_ai_response_and_analysis(history, user_context=user_context)
        
        reply_text = ai_data.get('reply', 'Извини, я задумался.')
        is_trigger = ai_data.get('is_trigger', False)
        new_title = ai_data.get('chat_title', 'Диалог')

        emotions = ai_data.get('emotions', {})
        anxiety_level = emotions.get('anxiety', 0.0)
        user_msg.anxiety = emotions.get('anxiety', 0.0)
        user_msg.sadness = emotions.get('sadness', 0.0)
        user_msg.anger = emotions.get('anger', 0.0)
        user_msg.apathy = emotions.get('apathy', 0.0)
        user_msg.primary_emotion = ai_data.get('primary_emotion', 'neutral')
        
        factors = ai_data.get('stress_factors', [])
        user_msg.stress_factors = ", ".join(factors) if isinstance(factors, list) else ""
        
        user_msg.is_trigger_alert = is_trigger
        user_msg.save()

        if session.title == "Новый чат":
            session.title = new_title
            session.save()
        
        needs_grounding = False
        # Порог уже правильный (0.85)
        if anxiety_level >= 0.85:
            needs_grounding = True
            reply_text += "\n\nЯ чувствую, что уровень твоей тревоги сейчас очень высок. Давай сделаем короткую паузу и выполним технику заземления. Это поможет вернуть контроль над телом."
        
        if is_trigger:
            reply_text = "Я вижу, что тебе невероятно тяжело. Пожалуйста, знай, что твоя жизнь важна. Обратись к специалистам прямо сейчас."

        Message.objects.create(session=session, sender='ai', text=reply_text, anxiety=anxiety_level)
        
        return JsonResponse({
            'response': reply_text,
            'is_trigger': is_trigger,
            'new_title': session.title,
            'needs_grounding': needs_grounding
        })
    
@login_required(login_url='/login/')
def delete_chat(request, session_id):
    if request.method == "POST":
        session = ChatSession.objects.filter(id=session_id, user=request.user).first()
        if session:
            session.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required(login_url='/login/')
def rename_chat(request, session_id):
    if request.method == "POST":
        session = ChatSession.objects.filter(id=session_id, user=request.user).first()
        if session:
            try:
                data = json.loads(request.body)
                new_title = data.get('title', '').strip()
                if new_title:
                    session.title = new_title
                    session.save()
                    return JsonResponse({'status': 'success', 'new_title': session.title})
            except json.JSONDecodeError:
                pass
    return JsonResponse({'status': 'error'}, status=400)