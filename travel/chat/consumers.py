import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from groups.models import ChatGroup
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_code = self.scope['url_route']['kwargs']['group_code']
        self.room_group_name = f'chat_{self.group_code}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username

        if not message.strip():
            return

        # Save message to database
        await self.save_message(self.scope['user'].id, self.group_code, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @database_sync_to_async
    def save_message(self, user_id, group_code, content):
        user = User.objects.get(id=user_id)
        group = ChatGroup.objects.get(code=group_code)
        Message.objects.create(sender=user, group=group, content=content)
