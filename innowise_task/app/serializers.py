from rest_framework import serializers

from app.models import Profile, Images, Location
from django.contrib.auth.models import User

class ProfileSerializer(serializers.ModelSerializer):

    images = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    location = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'fname', 'lname', 'info', 'vip', 'user', 'images', 'location', 'gender')
        read_only_fields = ('id', 'images', 'user', 'lname', 'fname', 'location')
        extra_kwargs = {
            'info': {'required':False}, 
            'vip': {'required':False},
            'gender': {'required':False}
            }

    def create(self, validated_data):
        validated_data['user_id'] = self.context['request'].user.id
        return super(ProfileSerializer, self).create(validated_data)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', )
        extra_kwargs = {
            'username': {'required':True},
            'first_name': {'required':True}, 
            'last_name': {'required':True},
            'password': {'required':True}, 
            'email':{'required':True}
            }
    
    def create(self, data):
        password = data.pop('password', None)
        instance = self.Meta.model(**data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class ImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Images
        fields = ('image', 'profile', 'date')
        read_only_fields = ('profile', 'date')


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ('profile', 'location', 'date', 'latitude', 'longitude')
        read_only_fields = ('profile', 'date')
        depth = 1