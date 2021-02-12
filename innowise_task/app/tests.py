import random

from django.urls import reverse
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from app.models import Profile, Location, Images
from pytest_factoryboy import register
from factory.django import DjangoModelFactory

import factory
import pytest

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

@register
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.LazyAttribute(
        lambda obj: '{}.{}'.format(
            obj.first_name.lower(), 
            obj.last_name.lower()
            )
        )
    email = factory.LazyAttribute(
        lambda obj: '{}.{}@example.com'.format(
            obj.first_name.lower(), 
            obj.last_name.lower()
            )
        )

@register
class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile

    fname = factory.Faker('first_name')
    lname = factory.Faker('last_name')
    info = factory.Faker('sentence')
    vip = False
    gender = random.choice(['F', 'M'])
    user = factory.SubFactory(UserFactory)

@register
class LocationFactory(DjangoModelFactory):
    class Meta:
        model = Location
    '''Minsk city coordinates'''
    location = ''
    latitude = 53.9
    longitude = 27.5667
    profile = factory.SubFactory(ProfileFactory)

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

'''
    Test whether access to various endpoints 
    available for authenticated users only
'''
@pytest.mark.django_db
@pytest.mark.parametrize(
    'endpoint', [
        'app:profile-list', 'app:location-list', 'app:images-list',
        'activities:swipe-list', 'chat:chat-list'
    ]
)
def test_unauthorized_request(endpoint, api_client):
    url = reverse(endpoint)
    response = api_client.get(url)
    assert response.status_code == 401

'''Create user with different credentails test'''
@pytest.mark.django_db
@pytest.mark.parametrize(
   'data, status_code', [
        pytest.param(
            ['test'], 400,
            id='only_username_provided'
            ),
        pytest.param(
            ['test', 'test'], 400,
            id='username_password_provided'
            ),
        pytest.param(
            ['test', 'test', 'Test', 'User', 'test@gmail.com'], 201,
            id='valid_credentials_provided'
            )
   ]
)
def test_create_user(data, status_code, api_client):
    url = reverse('register')
    fileds = ['username', 'password', 'first_name', 'last_name', 'email']
    new_data = dict(zip(fileds, data))
    response = api_client.post(url, data=new_data)
    assert response.status_code == status_code

'''
    Test whether profile and locations objects are created
    when new user is registered
'''
@pytest.mark.django_db
def test_create_user_data(api_client):
    keys = ['username', 'password', 'first_name', 'last_name', 'email']
    values = ['test', 'test', 'Test', 'User', 'test@gmail.com']
    url = reverse('register')
    data = dict(zip(keys, values))
    response = api_client.post(url, data=data)
    user = User.objects.get(id=response.data['id'])
    profile = Profile.objects.get(id=response.data['id'])
    location = Location.objects.get(id=response.data['id'])
    assert profile.user == user 
    assert location.profile == profile

'''Get info about authorized profile test'''
@pytest.mark.django_db
def test_get_self_profile_info(auth_client):
    url = reverse('app:profile-list') + '?me=true'
    response = auth_client.get(url)
    assert response.status_code == 200

'''Get info about unauthorized profile test'''
@pytest.mark.django_db
def test_get_self_unauthorized_profile_info(api_client):
    url = reverse('app:profile-list') + '?me=true'
    response = api_client.get(url)
    assert response.status_code == 401

'''Test whether there are no accounts yet'''
@pytest.mark.django_db
def test_get_profiles_no_users(auth_client):
    url = reverse('app:profile-list')
    response = auth_client.get(url)
    assert response.data['detail'] == 'no users found in the closest area'

'''
    Update authorized user profile test,
    update another user profile test
'''
@pytest.mark.django_db
def test_profile_update(auth_client):
    user_test: User = UserFactory()
    profile_test: Profile = ProfileFactory(fname=user_test.first_name, lname=user_test.last_name, user=user_test)
    location_test: Location = LocationFactory(profile=profile_test)
    get_profile_url = reverse('app:profile-list') + '?me=true'
    response = auth_client.get(get_profile_url)
    data = {
        'info':'Test info',
        'vip':'true',
        'gender':'F'
    }
    update_self_url = reverse('app:profile-detail', kwargs={'pk':response.data['id']})
    response = auth_client.put(update_self_url, data=data)
    assert response.status_code == 200
    update_fail_url = reverse('app:profile-detail', kwargs={'pk':profile_test.id})
    response = auth_client.put(update_fail_url, data=data)
    assert response.status_code == 400
    assert response.data['detail'] == 'user can update only it\'s profile'

'''
    Test whether location update calculates right coordinates
    and user can update it's location only once every two hours
'''
@pytest.mark.django_db
@pytest.mark.xfail(reason="Internet connection is needed")
def test_location_update(auth_client):   
    '''
        Test whether user can update it's location and
        coordinates will be calculated correctly,
        user can update it's location only once every two hours
    ''' 
    get_profile_url = reverse('app:profile-list') + '?me=true'
    response = auth_client.get(get_profile_url)

    location = 'Minsk, Belarus'

    geolocator = Nominatim(user_agent="InnowiseTaskApp")
    test_location = geolocator.geocode(location)

    url = reverse('app:location-detail', kwargs={'pk':response.data['location'][0]})
    data = {'location':location}
    response = auth_client.put(url, data=data)

    test_coordinates = (test_location.latitude, test_location.longitude)
    profile_coordinates = (response.data['latitude'], response.data['longitude'])
    assert test_coordinates == profile_coordinates

    response = auth_client.put(url, data=data)
    assert response.status_code == 400
    assert response.data['detail'] == 'location update available only once every two hours'

@pytest.mark.django_db
def test_location_update_other_user(auth_client):
    '''Test whether user cant update someone else location'''
    user_test: User = UserFactory()
    profile_test: Profile = ProfileFactory(fname=user_test.first_name, lname=user_test.last_name, user=user_test)
    location_test: Location = LocationFactory(profile=profile_test)

    url = reverse('app:location-detail', kwargs={'pk':location_test.id})
    data = {'location': 'Moscow, Russia'}
    response = auth_client.put(url, data=data)

    assert response.status_code == 400
    assert response.data['detail'] == 'user can update only its location'

@pytest.mark.django_db
@pytest.mark.xfail(reason="Internet connection is needed")
def test_get_random_profile(auth_client):
    '''
        Get random profile and check if this profile valid for
        current authenticated user according to his gender and location 
    '''
    get_profile_url = reverse('app:profile-list') + '?me=true'
    response = auth_client.get(get_profile_url)
    user_profile = Profile.objects.get(id=response.data['id'])

    radius = settings.VIP_SUBSCRIBTION_RADIUS if response.data['vip'] else settings.BASIC_SUBSCRIPTION_RADIUS
    user_coords = (
        user_profile.location.first().latitude, 
        user_profile.location.first().longitude
        )

    for i in range(5):
        user_test: User = UserFactory()
        gender = 'F' if user_profile.gender == 'M' else 'M'
        profile_test: Profile = ProfileFactory(
            fname=user_test.first_name, 
            lname=user_test.last_name, 
            user=user_test,
            gender=gender
            )
        location_test: Location = LocationFactory(location='Minsk, Belarus', profile=profile_test)

    url = reverse('app:profile-list')
    response = auth_client.get(url)
    assert len(Profile.objects.filter(id=response.data['id'])) == 1

    random_profile = Profile.objects.get(id=response.data['id'])
    profile_coords = (
        random_profile.location.first().latitude, 
        random_profile.location.first().longitude
        )

    assert geodesic(user_coords, profile_coords) < radius
