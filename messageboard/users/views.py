from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from django.core.paginator import Paginator

from .forms import CustomUserCreationForm, CustomUserChangeForm

User = get_user_model()


class RegisterView(CreateView):
    """Регистрация нового пользователя"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Регистрация успешно завершена! Теперь вы можете войти.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    """Личный профиль пользователя с пагинацией"""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        """Возвращает текущего пользователя"""
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from board.models import Ad
        
        # Получаем все объявления пользователя
        all_user_ads = Ad.objects.filter(
            author=self.request.user
        ).select_related('category').order_by('-created_at')
        
        # Активные объявления
        active_ads = all_user_ads.filter(
            is_active=True,
            published_until__gt=timezone.now()
        )
        
        # Просроченные объявления
        expired_ads = all_user_ads.filter(
            published_until__lt=timezone.now()
        )
        
        # Пагинация для объявлений
        paginator = Paginator(all_user_ads, 6)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['user_ads'] = page_obj
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['total_ads'] = all_user_ads.count()
        context['active_ads'] = active_ads.count()
        context['expired_ads'] = expired_ads.count()
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""
    model = User
    form_class = CustomUserChangeForm
    template_name = 'users/profile_edit.html'
    
    def get_object(self):
        """Возвращает текущего пользователя"""
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy('users:profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Ваш профиль успешно обновлен!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class PublicProfileView(DetailView):
    """Публичный профиль пользователя с пагинацией"""
    model = User
    template_name = 'users/public_profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def dispatch(self, request, *args, **kwargs):
        """Если пользователь смотрит свой профиль - редирект на личный"""
        username = self.kwargs.get('username')
        if request.user.is_authenticated and request.user.username == username:
            return redirect('users:profile')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        """Получаем пользователя по username"""
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from board.models import Ad
        
        user = self.get_object()
        
        # Получаем только активные объявления пользователя
        all_user_ads = Ad.objects.filter(
            author=user,
            is_active=True,
            published_until__gt=timezone.now()
        ).select_related('category').order_by('-created_at')
        
        # Статистика пользователя
        total_ads = all_user_ads.count()
        
        # Категории объявлений пользователя
        categories = all_user_ads.values('category__name', 'category__slug').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Пагинация для объявлений
        paginator = Paginator(all_user_ads, 6)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['user_ads'] = page_obj
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['total_ads'] = total_ads
        context['categories'] = categories
        context['is_own_profile'] = self.request.user.is_authenticated and self.request.user == user
        
        return context
