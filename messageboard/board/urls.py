from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    # Главная и общие страницы
    path('', views.AdListView.as_view(), name='ad_list'),
    path('about/', views.AboutView.as_view(), name='about'),
    
    # CRUD для объявлений
    path('ad/<int:pk>/', views.AdDetailView.as_view(), name='ad_detail'),
    path('ad/create/', views.AdCreateView.as_view(), name='ad_create'),
    path('ad/<int:pk>/edit/', views.AdUpdateView.as_view(), name='ad_update'),
    path('ad/<int:pk>/delete/', views.AdDeleteView.as_view(), name='ad_delete'),
    
    # Категории
    path('category/<slug:slug>/', views.CategoryAdsListView.as_view(), name='category_ads'),
    
    # Поиск
    path('search/', views.SearchAdsListView.as_view(), name='search'),
]
