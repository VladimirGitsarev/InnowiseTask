from rest_framework.routers import DefaultRouter
from django.urls import path, include

from app import views

app_name = 'app'

router = DefaultRouter()

router.register('images', views.ImagesViewSet)
router.register('profile', views.ProfileViewSet)
router.register('location', views.LocationViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 