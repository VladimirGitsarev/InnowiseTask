from rest_framework.routers import DefaultRouter
from django.urls import path, include

from chat import views

app_name = 'chat'

router = DefaultRouter()

router.register('chat', views.ChatViewSet, basename='chat')

urlpatterns = [
    path('', include(router.urls)),
] 