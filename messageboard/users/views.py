from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import User

class RegisterView(CreateView):
    """Регистрация нового пользователя"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Регистрация успешно завершена! Теперь вы можете войти.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)
