from rest_framework import serializers

from chat.models import Chat, Message

class ChatSerializer(serializers.ModelSerializer):
       
    class Meta:
        model = Chat
        fields = ('id', 'user1', 'user2', )
        read_only_fields = ('user1', 'user2', )
        depth = 1

class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('id', 'message', 'sender', 'chat', )
        depth = 1