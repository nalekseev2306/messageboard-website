from django.urls import path

from users.views import (
    LoginView,
    PasswordUpdateView,
    ProfileEditView,
    ProfileView,
    PublicProfileView,
    RegisterView,
    login_out,
)

app_name = 'users'


urlpatterns = [
    path('registration/', RegisterView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', login_out, name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('profile/password-change/', PasswordUpdateView.as_view(), name='password_change'),
    path('profile/<str:username>/', PublicProfileView.as_view(), name='public_profile'),
]
