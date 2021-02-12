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

import factory
import pytest

@register
class SwipeFactory(DjangoModelFactory):
    class Meta:
        model = Swipe

    liked = random.choice([True, False])
    profile = factory.SubFactory(ProfileFactory)
    swiped = factory.SubFactory(ProfileFactory)

'''Default API client'''
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
def test_get_empty_match_list(auth_client):
    url = reverse('activities:swipe-list')
    response = auth_client.get(url)

    assert response.status_code == 400
    assert response.data['detail'] == 'no matches yet'

@pytest.mark.django_db
def test_user_swipe(auth_client):
    '''User swipe test'''
    url = reverse('app:profile-list') + '?me=true'
    response = auth_client.get(url)
    id = response.data['id']

    user: User = UserFactory()
    profile: Profile = ProfileFactory(
        fname=user.first_name, 
        lname=user.last_name, 
        user=user,
        gender='F'
        )
    location: Location = LocationFactory(profile=profile)

    url = reverse('activities:swipe-list')
    data = {'swiped':profile.id, 'liked':True} 
    response = auth_client.post(url, data=data)

    assert response.status_code == 201
    assert response.data['swipe']['profile']['id'] == id
    assert response.data['swipe']['swiped']['id'] == profile.id

@pytest.mark.django_db
def test_already_swiped_user(auth_client):
    '''Test whether user already swiped user he wants to swipe now'''
    user: User = UserFactory()
    profile: Profile = ProfileFactory(
        fname=user.first_name, 
        lname=user.last_name, 
        user=user,
        gender='F'
        )
    location: Location = LocationFactory(profile=profile)

    url = reverse('activities:swipe-list')
    data = {'swiped':profile.id, 'liked':True} 
    response = auth_client.post(url, data=data)

    assert response.status_code == 201

    response_repeat = auth_client.post(url, data=data)
    
    assert response_repeat.status_code == 400
    assert response_repeat.data['detail'] == 'user have already swiped this profile'
    
@pytest.mark.django_db
def test_get_matches(auth_client):
    '''Test getting matches of current user'''
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

    swipe_user: Swipe = SwipeFactory(profile=user_profile, swiped=profile, liked=True)
    swipe: Swipe = SwipeFactory(profile=profile, swiped=user_profile, liked=True)

    url = reverse('activities:swipe-list')
    response = auth_client.get(url)

    assert (
        response.data[0]['profile']['id'] == profile.id
        and response.data[0]['swiped']['id'] == user_profile.id 
        )

@pytest.mark.django_db
def test_get_matched_profile(auth_client):
    '''Getting info of matched and unmatched users'''
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

    swipe_user: Swipe = SwipeFactory(profile=user_profile, swiped=profile, liked=True)
    swipe: Swipe = SwipeFactory(profile=profile, swiped=user_profile, liked=True)

    url = reverse('app:profile-detail', kwargs={'pk':profile.id})
    response = auth_client.get(url)

    assert response.status_code == 200

    user_unmatched: User = UserFactory()
    profile_unmatched: Profile = ProfileFactory(
        fname=user.first_name, 
        lname=user.last_name, 
        user=user,
        gender='F'
        )
    location_unmatched: Location = LocationFactory(profile=profile)

    url = reverse('app:profile-detail', kwargs={'pk':profile_unmatched.id})
    response = auth_client.get(url)

    assert response.status_code == 400
    assert response.data['detail'] == 'user can\'t get info about unmatched profile'


@pytest.mark.django_db
def test_swipe_limit(auth_client):
    '''Test whether user cant swipe anymore according to his subscription limit'''
    url = reverse('app:profile-list') + '?me=true'
    response = auth_client.get(url)
    user_profile = Profile.objects.get(id=response.data['id'])

    limit = settings.BASIC_SUBSCRIPTION_SWIPES if user_profile.vip else settings.VIP_SUBSCRIBTION_SWIPES
    gender = 'F' if user_profile.gender == 'M' else 'M'
    last_profile = None
    for i in range(limit+1):
        user: User = UserFactory()
        profile: Profile = ProfileFactory(
            fname=user.first_name, 
            lname=user.last_name, 
            user=user,
            gender=gender
        )
        location: Location = LocationFactory(profile=profile)
        if i == limit: 
            last_profile = profile
            break
        swipe = SwipeFactory(profile=user_profile, swiped=profile, liked=random.choice([True, False]))

    url = reverse('activities:swipe-list')
    data = {'swiped':last_profile.id, 'liked':True} 
    response = auth_client.post(url, data=data)

    assert response.status_code == 400
    assert response.data['detail'] == 'swipes limit is exceeded for today'
