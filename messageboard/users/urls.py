from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import (
    RegisterView, ProfileView,
    ProfileEditView, PublicProfileView
)

app_name = 'users'

urlpatterns = [
    # Регистрация, авторизация и др
    path('auth/password_reset/', 
         auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            success_url=reverse_lazy('users:password_reset_done')
         ), 
         name='password_reset'),
    
    path('auth/password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),

    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', RegisterView.as_view(), name='registration'),

    # Профили
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('profile/<str:username>/', PublicProfileView.as_view(), name='public_profile'),
]
