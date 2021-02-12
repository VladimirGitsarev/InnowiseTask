
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app.views import UserView, APIOverview

'''
    Use JWT authorization with simplejwt lib
    Add two endpoints to get access and refresh tokens
'''

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', APIOverview.as_view(), name='api_overview'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserView.as_view(), name='register'),
    path('api/app/', include('app.urls', namespace='app')),
    path('api/activities/', include('activities.urls', namespace='activities')),
    path('api/chat/', include('chat.urls', namespace='chat'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
