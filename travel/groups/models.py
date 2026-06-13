from django.db import models
from django.contrib.auth.models import User
import string
import random

def generate_unique_code():
    length = 6
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if ChatGroup.objects.filter(code=code).count() == 0:
            break
    return code

class ChatGroup(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=8, unique=True, default=generate_unique_code)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='chat_groups')
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Trip(models.Model):
    group = models.OneToOneField(ChatGroup, on_delete=models.CASCADE, related_name='trip')
    destination_city = models.CharField(max_length=100)
    destination_lat = models.FloatField(blank=True, null=True)
    destination_lon = models.FloatField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    hotel_name = models.CharField(max_length=100, blank=True, null=True)
    hotel_lat = models.FloatField(blank=True, null=True)
    hotel_lon = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.group.name} - {self.destination_city}"

class UserPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preferences')
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='preferences')
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    trip_style = models.CharField(max_length=50)
    age_group = models.CharField(max_length=20, default="25-35")
    mobility_constraints = models.BooleanField(default=False)
    category_votes = models.JSONField(default=dict)
    embedding = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"
