from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.views import View
from django.core.files.storage import default_storage

from .models import Ad, Category, AdImage, AdFile
from .forms import AdForm


class AdListView(ListView):
    """Список всех активных объявлений (главная страница)"""

    model = Ad
    template_name = 'board/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 9

    def get_queryset(self):
        """Показываем только активные объявления, сортируем по дате"""
        return (
            Ad.objects.filter(
                is_active=True, published_until__gt=timezone.now()
            )
            .select_related('category', 'author')
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем популярные категории для боковой панели
        context['popular_categories'] = (
            Category.objects.filter(is_active=True, ads__is_active=True)
            .annotate(ad_count=Count('ads'))
            .filter(ad_count__gt=0)
            .order_by('-ad_count')[:10]
        )

        context['recent_ads'] = self.get_queryset()[:6]
        context['title'] = 'Главная - Доска объявлений'
        return context


class AdDetailView(DetailView):
    """Детальная страница объявления"""

    model = Ad
    template_name = 'board/ad_detail.html'
    context_object_name = 'ad'

    def get_queryset(self):
        """Показываем объявление только если оно активно"""
        return (
            Ad.objects.filter(
                is_active=True, published_until__gt=timezone.now()
            )
            .select_related('category', 'author')
            .prefetch_related('images', 'files')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad = self.get_object()

        # Похожие объявления (по категории и типу)
        context['similar_ads'] = (
            Ad.objects.filter(
                category=ad.category,
                ad_type=ad.ad_type,
                is_active=True,
                published_until__gt=timezone.now(),
            )
            .exclude(pk=ad.pk)
            .select_related('category')[:4]
        )

        context['images_count'] = ad.images.count()
        context['files_count'] = ad.files.count()
        context['title'] = f'{ad.title} - Доска объявлений'

        return context


class AdCreateView(LoginRequiredMixin, CreateView):
    """Создание нового объявления"""

    model = Ad
    form_class = AdForm
    template_name = 'board/ad_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создать объявление'
        context['button_text'] = 'Опубликовать'
        return context

    def form_valid(self, form):
        """Привязываем автора"""
        ad = form.save(commit=False)
        ad.author = self.request.user
        ad.contact_phone = self.request.user.phone
        ad.contact_email = self.request.user.email
        ad.contact_name = self.request.user.get_full_name()
        ad.save()

        images = self.request.FILES.getlist('images')
        for idx, img in enumerate(images):
            AdImage.objects.create(
                ad=ad, image=img, is_main=False, order=ad.images.count() + idx
            )

        files = self.request.FILES.getlist('files')
        for idx, file in enumerate(files):
            AdFile.objects.create(
                ad=ad, file=file, order=ad.files.count() + idx
            )

        messages.success(self.request, 'Ваше объявление успешно опубликовано!')
        return redirect('board:ad_detail', pk=ad.pk)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме')
        return super().form_invalid(form)


class AdUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование объявления"""

    model = Ad
    form_class = AdForm
    template_name = 'board/ad_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать объявление'
        context['button_text'] = 'Сохранить изменения'
        context['existing_images'] = self.object.images.all()
        context['existing_files'] = self.object.files.all()
        return context

    def test_func(self):
        ad = self.get_object()
        return self.request.user.is_staff or ad.author == self.request.user

    def form_valid(self, form):
        ad = form.save()

        existing_images_count = ad.images.count()
        existing_files_count = ad.files.count()
        new_images = self.request.FILES.getlist('images')
        new_files = self.request.FILES.getlist('files')

        total_images = existing_images_count + len(new_images)
        if total_images > 4:
            messages.error(
                self.request,
                'Превышено максимальное количество изображений. Вы можете загрузить не более 4.',
            )
            return redirect('board:ad_update', pk=ad.pk)

        total_files = existing_files_count + len(new_files)
        if total_files > 4:
            messages.error(
                self.request,
                'Превышено максимальное количество файлов. Вы можете загрузить не более 4.',
            )
            return redirect('board:ad_update', pk=ad.pk)

        for idx, img in enumerate(new_images):
            AdImage.objects.create(
                ad=ad,
                image=img,
                is_main=False,
                order=existing_images_count + idx,
            )

        for idx, file in enumerate(new_files):
            AdFile.objects.create(
                ad=ad, file=file, order=existing_files_count + idx
            )

        messages.success(self.request, 'Объявление успешно обновлено!')
        return redirect('board:ad_detail', pk=ad.pk)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('board:ad_detail', kwargs={'pk': self.object.pk})


class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление объявления"""

    model = Ad
    template_name = 'board/ad_confirm_delete.html'
    success_url = reverse_lazy('board:ad_list')

    def test_func(self):
        """Только автор или админ может удалить"""
        ad = self.get_object()
        return self.request.user.is_staff or ad.author == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Объявление успешно удалено!')
        return super().delete(request, *args, **kwargs)


class CategoryAdsListView(ListView):
    """Объявления по категории"""

    model = Ad
    template_name = 'board/category_ads.html'
    context_object_name = 'ads'
    paginate_by = 9

    def get_queryset(self):
        """Фильтруем объявления по slug категории"""
        self.category = get_object_or_404(
            Category.objects.filter(is_active=True), slug=self.kwargs['slug']
        )
        return (
            Ad.objects.filter(
                category=self.category,
                is_active=True,
                published_until__gt=timezone.now(),
            )
            .select_related('author')
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['title'] = f'{self.category.name} - Доска объявлений'
        return context


class SearchAdsListView(ListView):
    """Поиск объявлений"""

    model = Ad
    template_name = 'board/search_results.html'
    context_object_name = 'ads'
    paginate_by = 9

    def get_queryset(self):
        """Реализуем поиск по заголовку, описанию, категории и городу"""
        queryset = Ad.objects.filter(
            is_active=True, published_until__gt=timezone.now()
        ).select_related('category', 'author')

        self.query = self.request.GET.get('q', '')
        self.category_id = self.request.GET.get('category', '')
        self.city = self.request.GET.get('city', '')
        self.ad_type = self.request.GET.get('ad_type', '')

        if self.query:
            queryset = queryset.filter(
                Q(title__icontains=self.query)
                | Q(description__icontains=self.query)
            )

        if self.category_id:
            queryset = queryset.filter(category_id=self.category_id)

        if self.city:
            queryset = queryset.filter(city__iregex=self.city)

        if self.ad_type:
            queryset = queryset.filter(ad_type=self.ad_type)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.query
        context['categories'] = Category.objects.filter(is_active=True)
        context['selected_category'] = self.category_id
        context['selected_city'] = self.city
        context['selected_ad_type'] = self.ad_type
        context['ad_types'] = Ad.AD_TYPE_CHOICES
        context['title'] = (
            f'Поиск: {self.query}' if self.query else 'Поиск объявлений'
        )
        return context


class DeleteImageView(LoginRequiredMixin, View):
    """Удаление изображения из БД и из media"""

    def post(self, request, pk):
        try:
            image = get_object_or_404(AdImage, pk=pk)
            ad = image.ad

            if request.user != ad.author and not request.user.is_staff:
                return JsonResponse(
                    {'success': False, 'error': 'У вас нет прав на удаление'},
                    status=403,
                )

            file_path = image.image.name
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            image.delete()

            return JsonResponse(
                {'success': True, 'message': 'Изображение удалено'}
            )

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class DeleteFileView(LoginRequiredMixin, View):
    """Удаление файла из БД и из media"""

    def post(self, request, pk):
        try:
            file_obj = get_object_or_404(AdFile, pk=pk)
            ad = file_obj.ad

            if request.user != ad.author and not request.user.is_staff:
                return JsonResponse(
                    {'success': False, 'error': 'У вас нет прав на удаление'},
                    status=403,
                )

            file_path = file_obj.file.name
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            file_obj.delete()
            return JsonResponse({'success': True, 'message': 'Файл удален'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class AboutView(TemplateView):
    """Страница о проекте"""

    template_name = 'board/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_ads'] = Ad.objects.filter(is_active=True).count()
        context['total_categories'] = Category.objects.filter(
            is_active=True
        ).count()
        context['title'] = 'О проекте'
        return context
