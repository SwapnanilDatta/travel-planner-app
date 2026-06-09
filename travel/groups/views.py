from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from .models import ChatGroup, Trip, UserPreference
from .forms import TripForm, UserPreferenceForm

from django.conf import settings

def get_coordinates(query, prox_lat=None, prox_lon=None):
    if not settings.OPENCAGE_API_KEY:
        print("Missing OPENCAGE_API_KEY")
        return None, None
    try:
        url = 'https://api.opencagedata.com/geocode/v1/json'
        params = {'q': query, 'key': settings.OPENCAGE_API_KEY, 'limit': 1}
        if prox_lat is not None and prox_lon is not None:
            params['proximity'] = f"{prox_lat},{prox_lon}"
        headers = {'User-Agent': 'GroupTravelPlannerApp/1.0'}
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200 and len(response.json().get('results', [])) > 0:
            data = response.json()['results'][0]['geometry']
            return float(data['lat']), float(data['lng'])
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None, None

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
            
            # Geocode Destination City
            city_lat, city_lon = get_coordinates(trip.destination_city)
            if city_lat is not None and city_lon is not None:
                trip.destination_lat = city_lat
                trip.destination_lon = city_lon
            
            # Geocode Hotel
            if trip.hotel_name:
                hotel_lat, hotel_lon = get_coordinates(trip.hotel_name, prox_lat=city_lat, prox_lon=city_lon)
                if hotel_lat is not None and hotel_lon is not None:
                    trip.hotel_lat = hotel_lat
                    trip.hotel_lon = hotel_lon
                else:
                    # Fallback to city coordinates
                    trip.hotel_lat = city_lat
                    trip.hotel_lon = city_lon
                    
            trip.save()
            messages.success(request, 'Trip created successfully (Geocoded)!')
            return redirect('group_detail', code=group.code)
    else:
        form = TripForm()
        
    return render(request, 'groups/create_trip.html', {
        'form': form, 
        'group': group,
        'opencage_api_key': settings.OPENCAGE_API_KEY
    })

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
        form = UserPreferenceForm(instance=existing_pref)
        
    return render(request, 'groups/submit_preference.html', {'form': form, 'group': group})
