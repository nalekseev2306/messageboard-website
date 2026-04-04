from django.urls import path
from . import views

app_name = 'board'  # пространство имен для обратных ссылок

urlpatterns = [
    # Главная и общая страницы
    path('', views.ad_list, name='ad_list'),
    path('about/', views.AboutView.as_view(), name='about'),
    
    # CRUD для объявлений
    path('ad/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('ad/create/', views.ad_create, name='ad_create'),
    path('ad/<int:pk>/edit/', views.ad_update, name='ad_update'),
    path('ad/<int:pk>/delete/', views.ad_delete, name='ad_delete'),
    
    # Категории
    path('category/<slug:slug>/', views.category_ads, name='category_ads'),
    
    # Поиск
    path('search/', views.search_ads, name='search'),
    
    # Мои объявления
    path('my-ads/', views.my_ads, name='my_ads'),
]
