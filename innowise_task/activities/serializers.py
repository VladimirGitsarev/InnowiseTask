from rest_framework import serializers

from app.models import Profile
from activities.models import Swipe

class SwipeSerializer(serializers.ModelSerializer):
       
    class Meta:
        model = Swipe
        fields = ('date', 'liked', 'profile', 'swiped')
        read_only_fields = ('date', )
        extra_kwargs = {
            'liked':{'required':True}
        }
        depth = 1

