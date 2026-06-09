from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChatGroup

@login_required
def home(request):
    groups = request.user.chat_groups.all()
    return render(request, 'groups/home.html', {'groups': groups})

@login_required
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            group = ChatGroup.objects.create(name=name, creator=request.user)
            group.members.add(request.user)
            messages.success(request, f'Group "{name}" created! Your code is {group.code}')
            return redirect('home')
    return render(request, 'groups/create_group.html')

@login_required
def join_group(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        if code:
            try:
                group = ChatGroup.objects.get(code=code)
                group.members.add(request.user)
                messages.success(request, f'You joined "{group.name}"!')
                return redirect('home')
            except ChatGroup.DoesNotExist:
                messages.error(request, 'Invalid group code.')
    return render(request, 'groups/join_group.html')
