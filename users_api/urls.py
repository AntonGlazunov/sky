from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users_api.apps import UsersApiConfig
from users_api.views import UserCreateAPIView, LoginAPIView

app_name = UsersApiConfig.name


urlpatterns = [
    path('create/', UserCreateAPIView.as_view(), name='users_create'),
    path('token/', LoginAPIView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]