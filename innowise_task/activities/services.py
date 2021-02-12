from datetime import datetime, timedelta

from django.db.models.query import QuerySet
from django.conf import settings

from app.models import Profile
from activities.models import Swipe

def get_matches(request) -> QuerySet:
    '''
        Get matches for current user, check if current user was liked by another 
        and filter swipes by getting profiles liked by the user
    '''
    profile = Profile.objects.get(user=request.user)
    liked = Swipe.objects.filter(liked=True, profile=profile)
    profiles: list = [like.swiped for like in  liked]
    matches = Swipe.objects.filter(liked=True, swiped=profile, profile__in=profiles)
    return matches

def is_swipe_available(profile) -> bool:
    '''
        Check if user subscription allows it to make one more swipe
        by getting an amount of today's swipes
    '''
    swipe_count_available = settings.VIP_SUBSCRIBTION_SWIPES if profile.vip else settings.BASIC_SUBSCRIPTION_SWIPES
    return Swipe.objects.filter(
        date__contains=datetime.strftime(datetime.today(), '%Y-%m-%d'),
        profile=profile
        ).count() < swipe_count_available

def is_already_swiped(profile, swiped) -> bool:
    '''Check if user already swiped this profile'''
    return len(profile.swipes.filter(swiped=swiped)) != 0

def is_match(profile, swiped, liked) -> bool:
    '''Check if users are matched'''
    if not liked:
        return False
    return len(swiped.swipes.filter(swiped=profile, liked=True)) != 0

