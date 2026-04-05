from django.urls import path, include
from .views import RegisterView

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('registration/', RegisterView.as_view(), name='registration'),
]
