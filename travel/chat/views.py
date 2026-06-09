from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from groups.models import ChatGroup
from .models import Message

@login_required
def chat_room(request, group_code):
    group = get_object_or_404(ChatGroup, code=group_code)
    
    # Check if user is a member
    if request.user not in group.members.all():
        messages.error(request, "You are not a member of this group.")
        return redirect('home')
        
    messages_list = group.messages.all()
    
    return render(request, 'chat/room.html', {
        'group': group,
        'messages_list': messages_list
    })
