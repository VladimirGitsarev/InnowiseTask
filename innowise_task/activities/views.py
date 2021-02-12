from django.shortcuts import render
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from activities.models import Swipe
from activities.serializers import SwipeSerializer
from activities.services import (
    get_matches, 
    is_swipe_available, 
    is_already_swiped,
    is_match
)
from app.models import Profile
from chat.models import Chat

class SwipeViewSet(viewsets.GenericViewSet, 
                    mixins.ListModelMixin, 
                    mixins.CreateModelMixin):
    serializer_class = SwipeSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Swipe.objects.all()

    def list(self, request):
        '''Get list of matches'''
        matches = get_matches(request)
        serializer = self.get_serializer(matches, many=True)
        if len(serializer.data) != 0:
            return Response(serializer.data, status=status.HTTP_200_OK)
        message = {'detail': 'no matches yet'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
        
    def create(self, request):
        '''
            Create swipe object when user swipes another user
            If user are matched create a chat object to let users 
            chat with each other
        '''
        profile = Profile.objects.get(user=request.user)
        if is_swipe_available(profile):
            try:
                swiped = Profile.objects.get(id=request.data['swiped'])
                if is_already_swiped(profile, swiped):
                    message = {'detail':'user have already swiped this profile'}
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
            except:
                message = {'detail':'pleace, specify the \"swiped\" field'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(profile=profile, swiped=swiped)
                try:
                    if is_match(profile, swiped, request.data['liked']):
                        chat = Chat.objects.create(
                            user1=profile,
                            user2=swiped
                        )
                        chat.save()
                    message = {
                        'match': is_match(profile, swiped, request.data['liked']),
                        'swipe': serializer.data
                    }
                except:
                    message = {'detail':'pleace, specify the \"liked\" field'}
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
                return Response(message, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        message = {'detail':'swipes limit is exceeded for today'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    