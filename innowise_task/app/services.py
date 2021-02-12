
import uuid
import os
import random

from datetime import datetime, timezone
from django.conf import settings

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

def image_file_path(instance, filename) -> str:
    '''Generate file path for new image'''
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('upload/profile/', filename)

def is_location_update_time_valid(instance) -> bool:
    '''
        Check if it's enough time passed to update 
        user location or if location is empty
    '''
    if instance.location == '':
        return True
    secs_in_hour = 3600
    return (datetime.now(timezone.utc) - instance.date).seconds//secs_in_hour >= settings.LOCATION_UPDATE_HOURS

def is_profile_updating_self(profile, instance) -> bool:
    '''Check if user updates itself'''
    return profile == instance

def is_location_updating_self(instance, profile) -> bool:
    '''Check if user updates its location'''
    return instance.profile == profile

def is_info_availbale(obj, profile) -> bool:
    '''
        Check if requested user was liked by current user
        and current user was liked by requested user
    '''
    user_like = profile.swipes.filter(swiped=obj, liked=True).first()
    obj_like = obj.swiped.filter(profile=profile, liked=True).first()
    if user_like and obj_like:
        return user_like == obj_like
    return False

def get_coordinates(location) -> tuple:
    '''
        Use geopy lib for getting users geolocation
        User location stored as the name of the country, town etc.
        Get coordinates using stored user location and 
    '''
    geolocator = Nominatim(user_agent="InnowiseTaskApp")
    profile_location = geolocator.geocode(location)
    return profile_location.latitude, profile_location.longitude

def get_random_profile(queryset, profile):
    '''
        Check whethere people are around the area, specified in user subscription
        and filter already swiped profiles
        Return random found profile of opposite gender
    '''
    profile_coords = (profile.location.first().latitude, profile.location.first().longitude)
    radius = settings.VIP_SUBSCRIBTION_RADIUS if profile.vip else settings.BASIC_SUBSCRIPTION_RADIUS
    swiped_profiles = [swipe.swiped.id for swipe in profile.swipes.all()]

    profiles = queryset\
        .exclude(user=profile.user)\
        .exclude(gender=profile.gender)\
        .exclude(id__in=swiped_profiles)
    
    filtered_profiles = []
    for profile in profiles:
        distance = geodesic(profile_coords, (
            profile.location.first().latitude, 
            profile.location.first().longitude)
            )
        if distance < radius:
            filtered_profiles.append(profile)
            
    return random.choice(filtered_profiles) if len(filtered_profiles) !=0 else None
