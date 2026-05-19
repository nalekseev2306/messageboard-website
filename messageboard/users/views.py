from board.models import Ad
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import PasswordChangeView
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, UpdateView

from users.constants import (
    MSG_ERROR_PROFILE_EDIT,
    MSG_ERROR_REGISTER,
    MSG_SUCCESS_PASSWORD_CHANGE,
    MSG_SUCCESS_PROFILE_EDIT,
    MSG_SUCCESS_REGISTER,
    PUBLIC_PROFILE_PAGE_SIZE,
    SELF_PROFILE_PAGE_SIZE,
)
from users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


class RegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, MSG_SUCCESS_REGISTER)
        return response

    def form_invalid(self, form):
        messages.error(self.request, MSG_ERROR_REGISTER)
        return super().form_invalid(form)


class LoginView(BaseLoginView):
    template_name = 'registration/login.html'
    next_page = 'board:ad_list'


def login_out(request):
    logout(request)
    return redirect('board:ad_list')


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_user_ads = (
            Ad.objects.filter(author=self.request.user)
            .select_related('category')
            .order_by('-created_at')
        )

        active_ads = all_user_ads.filter(is_active=True, published_until__gt=timezone.now())
        expired_ads = all_user_ads.filter(published_until__lt=timezone.now())

        paginator = Paginator(all_user_ads, SELF_PROFILE_PAGE_SIZE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['user_ads'] = page_obj
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['total_ads'] = all_user_ads.count()
        context['active_ads'] = active_ads.count()
        context['expired_ads'] = expired_ads.count()

        return context


class PasswordUpdateView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'registration/password_change_form.html'

    def get_success_url(self):
        messages.success(self.request, MSG_SUCCESS_PASSWORD_CHANGE)
        return reverse('users:profile')


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = 'users/profile_edit.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def form_valid(self, form):
        messages.success(self.request, MSG_SUCCESS_PROFILE_EDIT)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, MSG_ERROR_PROFILE_EDIT)
        return super().form_invalid(form)


class PublicProfileView(DetailView):
    model = User
    template_name = 'users/public_profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def dispatch(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        if request.user.is_authenticated and request.user.username == username:
            return redirect('users:profile')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username, is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        all_user_ads = (
            Ad.objects.filter(author=user, is_active=True, published_until__gt=timezone.now())
            .select_related('category')
            .order_by('-created_at')
        )
        categories = (
            all_user_ads.values('category__name', 'category__slug')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        total_ads = all_user_ads.count()

        paginator = Paginator(all_user_ads, PUBLIC_PROFILE_PAGE_SIZE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['user_ads'] = page_obj
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['total_ads'] = total_ads
        context['categories'] = categories
        context['is_own_profile'] = (
            self.request.user.is_authenticated and self.request.user == user
        )

        return context
