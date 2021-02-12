import random

from django.urls import reverse
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings
from rest_framework.test import APIClient
from pytest_factoryboy import register
from factory.django import DjangoModelFactory
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from app.tests import ProfileFactory, UserFactory, LocationFactory
from app.models import Profile, Location, Images
from activities.models import Swipe
from activities.tests import SwipeFactory
from chat.models import Chat, Message

import factory
import pytest

@register
class ChatFactory(DjangoModelFactory):
    class Meta:
        model = Chat

    user1 = factory.SubFactory(ProfileFactory)
    user2 = factory.SubFactory(ProfileFactory)

@register
class MessageFactory(DjangoModelFactory):
    class Meta:
        model = Message

    message = factory.Faker('sentence')
    sender = factory.SubFactory(ProfileFactory)
    chat = factory.SubFactory(ChatFactory)

@pytest.fixture
def api_client():
    return APIClient()

'''API client with authenticated user'''
@pytest.fixture
def auth_client():
    client = APIClient()
    user: User = UserFactory()
    profile: Profile = ProfileFactory(fname=user.first_name, lname=user.last_name, user=user)
    location: Location = LocationFactory(profile=profile)
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client

@pytest.mark.django_db
def test_create_chat_on_match(auth_client):
    '''Test whether new chat created when users are matched'''
    url = reverse('app:profile-list') + '?me=true'
    response = auth_client.get(url)
    user_profile = Profile.objects.get(id=response.data['id'])
    
    user: User = UserFactory()
    profile: Profile = ProfileFactory(
        fname=user.first_name, 
        lname=user.last_name, 
        user=user,
        gender='F'
        )
    location: Location = LocationFactory(profile=profile)

    swipe: Swipe = SwipeFactory(profile=profile, swiped=user_profile, liked=True)

    url = reverse('activities:swipe-list')
    data = {'swiped':profile.id, 'liked':True} 
    response = auth_client.post(url, data=data)

    assert response.status_code == 201
    assert response.data['match'] == True
    assert Chat.objects.filter(user1=user_profile, user2=profile).count() == 1

@pytest.mark.django_db
def test_get_user_chats(auth_client):
    '''Test if user gets all chat he tooks part in'''
    users_count = random.randrange(1, 10)

    url = reverse('app:profile-list') + '?me=true'
    response = auth_client.get(url)
    user_profile = Profile.objects.get(id=response.data['id'])

    for i in range(users_count):
        user: User = UserFactory()
        profile: Profile = ProfileFactory(
            fname=user.first_name, 
            lname=user.last_name, 
            user=user,
            gender='F'
            )
        location: Location = LocationFactory(profile=profile)
        if i % 2 == 0:
            chat: Chat = ChatFactory(user1=user_profile, user2=profile)
        else:
            chat: Chat = ChatFactory(user1=profile, user2=user_profile)

    url = reverse('chat:chat-list')
    response = auth_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == users_count

@pytest.mark.django_db
def test_send_message(auth_client):
    '''
        Test whether user can send message
        and it's sent to correct chat
    '''
    url = reverse('app:profile-list') + '?me=true'
    response = auth_client.get(url)
    user_profile = Profile.objects.get(id=response.data['id'])
    
    user: User = UserFactory()
    profile: Profile = ProfileFactory(
        fname=user.first_name, 
        lname=user.last_name, 
        user=user,
        gender='F'
        )
    location: Location = LocationFactory(profile=profile)

    chat: Chat = ChatFactory(user1=user_profile, user2=profile)

    url = reverse('chat:chat-list')
    data = {'chat':chat.id, 'message':'Hello world!'}
    response = auth_client.post(url, data=data)

    assert response.status_code == 201
    assert response.data['sender']['id'] == user_profile.id
    assert response.data['chat']['id'] == chat.id

@pytest.mark.django_db
def test_send_message_to_wrong_chat(auth_client):
    '''Send message to chat user is not in'''
    chat: Chat = ChatFactory(
        user1=ProfileFactory(),
        user2=ProfileFactory()
    )

    url = reverse('chat:chat-list')
    data = {'chat':chat.id, 'message':'Hello world!'}
    response = auth_client.post(url, data=data)

    assert response.status_code == 400
    assert response.data['detail'] == 'user can\'t chat with unmatched users'

@pytest.mark.django_db
def test_get_messages_from_chat(auth_client):
    '''Get messages from user specified chat test'''
    url = reverse('app:profile-list') + '?me=true'
    response = auth_client.get(url)
    user_profile = Profile.objects.get(id=response.data['id'])
    
    user: User = UserFactory()
    profile: Profile = ProfileFactory(
        fname=user.first_name, 
        lname=user.last_name, 
        user=user,
        gender='F'
        )
    location: Location = LocationFactory(profile=profile)

    chat: Chat = ChatFactory(user1=user_profile, user2=profile)

    messages_count = random.randint(1, 10)
    for i in range(messages_count):
        message = factory.Faker('sentence')
        if i % 2 == 0:
            user = user_profile
        else:
            user = profile
        message: Message = MessageFactory(message=message, sender=user, chat=chat)

    url = reverse('chat:chat-detail', kwargs={'pk':chat.id})
    response = auth_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == messages_count

@pytest.mark.django_db
def test_get_messages_from_wrong_chat(auth_client):

    chat: Chat = ChatFactory(user1=ProfileFactory(), user2=ProfileFactory())
    url = reverse('chat:chat-detail', kwargs={'pk':chat.id})
    response = auth_client.get(url)
    
    assert response.status_code == 400
    assert response.data['detail'] == 'user can\'t get messages from a chat he is not in'

