from django.urls import path, include
from .views import (
    RegisterView, ProfileView,
    ProfileEditView, PublicProfileView
)

app_name = 'users'

urlpatterns = [
    # Регистрация, авторизация и др
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', RegisterView.as_view(), name='registration'),

    # Профили
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('profile/<str:username>/', PublicProfileView.as_view(), name='public_profile'),
]
