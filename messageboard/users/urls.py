from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views

from .views import (
    RegisterView, ProfileView,
    ProfileEditView, PublicProfileView
)

app_name = 'users'

urlpatterns = [
    # Регистрация, авторизация
    path('auth/registration/', RegisterView.as_view(), name='registration'),
    path('auth/login/', 
         auth_views.LoginView.as_view(
            template_name='registration/login.html'
         ), 
         name='login'),
    path('auth/logout/', 
         auth_views.LogoutView.as_view(
            next_page='users:login'
         ), 
         name='logout'),
    # Смена пароля
    path('auth/password-change/',
         auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change_form.html',
            success_url=reverse_lazy('users:password_change_done')
         ),
         name='password_change'
    ),
    path('auth/password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html'
         ),
         name='password_change_done'
    ),
    # Восстановление пароля (только визуал)
    path('auth/password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            success_url=reverse_lazy('users:password_reset_done'),
        ),
        name='password_reset',
    ),
    path('auth/password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path('auth/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_reset_complete')
         ),
         name='password_reset_confirm'
    ),
    # Профили
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path(
        'profile/<str:username>/',
        PublicProfileView.as_view(),
        name='public_profile',
    ),
]
