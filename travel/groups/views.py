from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChatGroup, Trip, UserPreference
from .forms import TripForm, UserPreferenceForm

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
                if group.is_locked:
                    messages.error(request, 'This group is locked and no longer accepting members.')
                    return redirect('home')
                group.members.add(request.user)
                messages.success(request, f'You joined "{group.name}"!')
                return redirect('home')
            except ChatGroup.DoesNotExist:
                messages.error(request, 'Invalid group code.')
    return render(request, 'groups/join_group.html')

@login_required
def group_detail(request, code):
    group = get_object_or_404(ChatGroup, code=code)
    if request.user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('home')
    
    trip = getattr(group, 'trip', None)
    has_submitted_preference = UserPreference.objects.filter(group=group, user=request.user).exists()
    
    context = {
        'group': group,
        'trip': trip,
        'has_submitted_preference': has_submitted_preference,
        'is_host': request.user == group.creator,
    }
    return render(request, 'groups/group_detail.html', context)

@login_required
def lock_group(request, code):
    group = get_object_or_404(ChatGroup, code=code)
    if request.user == group.creator:
        group.is_locked = True
        group.save()
        messages.success(request, 'Group is now locked.')
    return redirect('group_detail', code=group.code)

@login_required
def create_trip(request, code):
    group = get_object_or_404(ChatGroup, code=code)
    if request.user != group.creator:
        messages.error(request, 'Only the host can create a trip.')
        return redirect('group_detail', code=group.code)
    if hasattr(group, 'trip'):
        messages.error(request, 'Trip already exists.')
        return redirect('group_detail', code=group.code)
        
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.group = group
            trip.save()
            messages.success(request, 'Trip created successfully!')
            return redirect('group_detail', code=group.code)
    else:
        form = TripForm()
        
    return render(request, 'groups/create_trip.html', {'form': form, 'group': group})

@login_required
def submit_preference(request, code):
    group = get_object_or_404(ChatGroup, code=code)
    if request.user not in group.members.all():
        return redirect('home')
        
    existing_pref = UserPreference.objects.filter(group=group, user=request.user).first()
    
    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=existing_pref)
        if form.is_valid():
            pref = form.save(commit=False)
            pref.user = request.user
            pref.group = group
            pref.save()
            messages.success(request, 'Preferences saved!')
            return redirect('group_detail', code=group.code)
    else:
        initial = {}
        if existing_pref and existing_pref.interests:
            initial['interests_str'] = ', '.join(existing_pref.interests)
        form = UserPreferenceForm(instance=existing_pref, initial=initial)
        
    return render(request, 'groups/submit_preference.html', {'form': form, 'group': group})
