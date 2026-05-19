from django.urls import path

from board.views import (
    AboutView,
    AdCreateView,
    AdDeleteView,
    AdDetailView,
    AdListView,
    AdUpdateView,
    CategoryAdListView,
    DeleteFileView,
    DeleteImageView,
    SearchAdListView,
)

app_name = 'board'


urlpatterns = [
    path('', AdListView.as_view(), name='ad_list'),
    path('about/', AboutView.as_view(), name='about'),
    path('ad/create/', AdCreateView.as_view(), name='ad_create'),
    path('ad/<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
    path('ad/<int:pk>/edit/', AdUpdateView.as_view(), name='ad_update'),
    path('ad/<int:pk>/delete/', AdDeleteView.as_view(), name='ad_delete'),
    path('category/<slug:slug>/', CategoryAdListView.as_view(), name='category_ads'),
    path('search/', SearchAdListView.as_view(), name='search'),
    path('image/<int:pk>/delete/', DeleteImageView.as_view(), name='delete_image'),
    path('file/<int:pk>/delete/', DeleteFileView.as_view(), name='delete_file'),
]
