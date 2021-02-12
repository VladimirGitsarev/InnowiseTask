from rest_framework.routers import DefaultRouter
from django.urls import path, include

from activities import views

app_name = 'activities'

router = DefaultRouter()

router.register('swipe', views.SwipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 