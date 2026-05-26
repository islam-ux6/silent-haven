import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import ChatSession, Message
from .ai_services import get_ai_response_and_analysis
from .forms import CustomUserCreationForm

def chat_interface(request):
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
            current_session = ChatSession.objects.create(user=request.user, title="New Chat")
    
    messages = Message.objects.filter(session=current_session).order_by('timestamp')
    
    return render(request, 'chat/index.html', {
        'sessions': sessions,
        'current_session': current_session,
        'messages': messages
    })

@login_required
def start_new_chat(request):
    new_session = ChatSession.objects.create(user=request.user, title="New Chat")
    return redirect('chat_with_id', session_id=new_session.id)

@login_required(login_url='/login/')
def send_message(request):
    if request.method == "POST":
        user_text = request.POST.get('message')
        session_id = request.POST.get('session_id')
        
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=400)
        
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

            user_context = f"""
            [SECRET CONTEXT FOR AI]: 
            Recently, the user's average anxiety level is: {avg_anx:.2f} out of 1.0. 
            Recent stress factors: {', '.join(top_recent_factors)}. 
            INSTRUCTION: Use this context only for maintaining the dialogue. Evaluate JSON emotions (anxiety) STRICTLY based on the last message, do not copy past average anxiety!
            """
            
        ai_data = get_ai_response_and_analysis(history, user_context=user_context)
        
        reply_text = ai_data.get('reply', 'Sorry, I was lost in thought.')
        is_trigger = ai_data.get('is_trigger', False)
        new_title = ai_data.get('chat_title', 'Dialogue')

        emotions = ai_data.get('emotions') or {}
        anxiety_level = emotions.get('anxiety') or 0.0
        
        user_msg.anxiety = emotions.get('anxiety') or 0.0
        user_msg.sadness = emotions.get('sadness') or 0.0
        user_msg.anger = emotions.get('anger') or 0.0
        user_msg.apathy = emotions.get('apathy') or 0.0
        
        user_msg.primary_emotion = ai_data.get('primary_emotion') or 'neutral'
        
        factors = ai_data.get('stress_factors') or []
        user_msg.stress_factors = ", ".join(factors) if isinstance(factors, list) else ""
        
        user_msg.is_trigger_alert = is_trigger
        user_msg.save()

        if session.title in ["New Chat", "Новый чат"]:
            session.title = new_title
            session.save()
        
        needs_grounding = False
        if anxiety_level >= 0.85:
            needs_grounding = True
            reply_text += "\n\nI feel that your anxiety level is very high right now. Let's take a short pause and do a grounding technique. This will help you regain control."
        
        if is_trigger:
            reply_text = "I see that you are going through an incredibly hard time. Please know that your life matters. Reach out to a professional or an emergency hotline right now."

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