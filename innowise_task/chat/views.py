from django.shortcuts import render
from django.db.models import Q

from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from chat.models import Chat, Message
from chat.serializers import ChatSerializer, MessageSerializer
from chat.services import is_chat_available
from app.models import Profile

class ChatViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        '''
            Get a list of chats available for current user
            Can chat only with matched users
        '''
        profile = Profile.objects.get(user=request.user)
        chats = Chat.objects.filter(
            Q(user1=profile) | Q(user2=profile)
        )
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        '''Send new message to chat'''
        profile = Profile.objects.get(user=request.user)
        serializer = MessageSerializer(data=request.data)
        try:
            chat = Chat.objects.get(id=request.data['chat'])
        except:
            message = {'detail':'pleace, specify the \"chat\" field'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            if is_chat_available(profile, chat):
                serializer.save(sender=profile, chat=chat)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            message = {'detail':'user can\'t chat with unmatched users'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        '''Get all messages from the specified chat'''
        profile = Profile.objects.get(user=request.user)
        chat = Chat.objects.get(id=pk)
        if is_chat_available(profile, chat):
            messages = Message.objects.filter(chat_id=pk).order_by('-date')
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        message = {'detail':'user can\'t get messages from a chat he is not in'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
