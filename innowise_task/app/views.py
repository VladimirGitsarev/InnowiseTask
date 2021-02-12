from django.shortcuts import render
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import os

from app.models import Profile, Images, Location
from app.serializers import ProfileSerializer, UserSerializer, ImagesSerializer, LocationSerializer
from app.services import (
    is_location_update_time_valid, 
    is_profile_updating_self, 
    is_location_updating_self,
    is_info_availbale,
    get_random_profile,
    get_coordinates
)

from os.path import join, dirname

class ProfileViewSet(viewsets.GenericViewSet, 
                    mixins.ListModelMixin, 
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Profile.objects.all()
        
    def list(self, request):
        '''Get current authenticated user by checking params'''
        if request.GET:
            return Response(
                self.get_serializer(
                    self.queryset.filter(user=self.request.user).first()
                ).data
            ) if 'me' in request.GET else Response(status=status.HTTP_400_BAD_REQUEST)

        '''Get random user around current user to like or dislike it'''
        profile = get_random_profile(
            self.get_queryset(), 
            self.queryset.filter(user=self.request.user).first()
            )
        if profile:
            serializer = self.get_serializer(self.get_queryset().filter(user=profile.user).first())
            return Response(serializer.data)
        message = {'detail':'no users found in the closest area'}
        return Response(message, status=status.HTTP_200_OK)

    def update(self, request, pk):
        '''Update profile if user updates itself'''
        instance = self.get_object()
        profile = self.queryset.filter(user=self.request.user).first()
        if is_profile_updating_self(instance, profile):
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        message = {'detail':'user can update only it\'s profile'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)   

    def retrieve(self, request, pk):
        '''Get profile info if users are matched'''
        instance = self.get_object()
        profile = self.queryset.filter(user=self.request.user).first()
        if is_info_availbale(instance, profile):
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        message = {'detail':'user can\'t get info about unmatched profile'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
        
class LocationViewSet(viewsets.GenericViewSet, 
                    mixins.ListModelMixin, 
                    mixins.UpdateModelMixin):
    serializer_class = LocationSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Location.objects.all()

    def list(self, request):
        '''Get current authenticated user location'''
        profile = Profile.objects.get(user=self.request.user)
        serializer = self.get_serializer(self.get_queryset().filter(profile=profile).first())
        return Response(serializer.data)

    def update(self, request, pk):
        '''
            Update current authenticated user location, 
            calculate coordinates according to user location
        '''
        instance = self.get_object()
        profile = Profile.objects.get(user=self.request.user)
        if is_location_updating_self(instance, profile):
            if is_location_update_time_valid(instance):
                try:
                    lat, lon = get_coordinates(request.data['location'])
                    serializer = self.get_serializer(instance, data={
                        'location': request.data['location'],
                        'latitude': float(lat),
                        'longitude': float(lon)
                    })
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except:
                    if 'location' in request.data:
                        message = {'detail':'try another location'}
                    else:
                        message = {'detail':'please, specify the location'}
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
            message = {'detail':'location update available only once every two hours'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {'detail':'user can update only its location'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

class ImagesViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     ):
    serializer_class = ImagesSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Images.objects.all()

    def list(self, request):
        """Return images for current authenticated user only"""
        profile = Profile.objects.get(user=request.user)
        serializer = self.get_serializer(self.get_queryset().filter(profile=profile), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """Add new image"""
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(profile=profile)

class UserView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        """Register new user and create user profile"""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile = Profile.objects.create(
                user=user, 
                fname=user.first_name, 
                lname=user.last_name
                )
            profile.save()
            location = Location.objects.create(profile=profile)
            location.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class APIOverview(APIView):
    permission_classes = (AllowAny, )

    def get(self, request):
        endpoints = {
            'api/token/': {
                'POST':'Get access JWT-token to authenticate, credentials are provided'
            },
            'api/token/refresh':{
                'POST':'Get refresh JWT-token to authenticate'
            },
            'register/':{
                'POST':'Register new user, credentials are provided'
            },
            'api/app/':{
                'profile?me=true':{
                    'GET':'Get info about current authenticated profile'
                },
                'profile/':{
                    'GET':'Get random profile of opposite gender and near the user',
                    'GET {pk}':'Get info about profile only if current user is matched with requested user',
                    'PUT {pk}':'Update info about the profile, only if authenticated'
                },
                'location/':{
                    'GET':'Get current authenticated user location',
                    'PUT {pk}':'Update current authenticated user location'
                },
                'images/':{
                    'GET':'Get images of current authenticated user',
                    'GET {pk}':'Get image specified in request',
                    'POST':'Save new image for current user'
                }
            },
            'api/activities/':{
                'swipe/':{
                    'GET':'Get list of matches for current user',
                    'POST':'Create a swipe object when user makes swipe',
                }
            },
            'api/chat/':{
                'chat/':{
                    'GET':'Get a list of chats available for current user',
                    'GET {pk}':'Get messages from a chat specified in the request',
                    'POST':'Send new message to a chat',
                }
            }
        }
        return Response(endpoints, status=status.HTTP_200_OK)
