from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files.storage import default_storage
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from board.constants import (
    ABOUT_TITLE,
    AD_LIST_TITLE,
    CATEGORY_LIST_TITLE,
    CREATE_BUTTON_TEXT,
    CREATE_TITLE,
    DETAIL_TITLE,
    MSG_ERROR_CREATE,
    MSG_ERROR_FILE,
    MSG_ERROR_IMAGE,
    MSG_ERROR_UPDATE,
    MSG_PERMISSION_DENIED,
    MSG_SUCCESS_CREATE,
    MSG_SUCCESS_DELETE,
    MSG_SUCCESS_FILE,
    MSG_SUCCESS_IMAGE,
    MSG_SUCCESS_UPDATE,
    PAGE_SIZE,
    UPDATE_BUTTON_TEXT,
    UPDATE_TITLE,
)
from board.forms import AdForm
from board.models import Ad, AdFile, AdImage, Category


class AdListView(ListView):
    model = Ad
    template_name = 'board/ad_list.html'
    context_object_name = 'ads'
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        return (
            Ad.objects.filter(is_active=True, published_until__gt=timezone.now())
            .select_related('category', 'author')
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_categories'] = (
            Category.objects.filter(is_active=True, ads__is_active=True)
            .annotate(ad_count=Count('ads'))
            .filter(ad_count__gt=0)
            .order_by('-ad_count')[:10]
        )
        context['title'] = AD_LIST_TITLE
        return context


class AdDetailView(DetailView):
    model = Ad
    template_name = 'board/ad_detail.html'
    context_object_name = 'ad'

    def get_queryset(self):
        queryset = Ad.objects.select_related('category', 'author').prefetch_related(
            'images', 'files'
        )

        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(is_active=True, published_until__gt=timezone.now()) | Q(author=self.request.user)
            )

        return queryset.filter(is_active=True, published_until__gt=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad = self.get_object()

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
        context['title'] = DETAIL_TITLE.format(title=ad.title)
        return context


class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = AdForm
    template_name = 'board/ad_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = CREATE_TITLE
        context['button_text'] = CREATE_BUTTON_TEXT
        return context

    def form_valid(self, form):
        ad = form.save(commit=False)
        ad.author = self.request.user
        ad.save()

        images = self.request.FILES.getlist('images')
        for idx, img in enumerate(images):
            AdImage.objects.create(ad=ad, image=img, order=ad.images.count() + idx)

        files = self.request.FILES.getlist('files')
        for idx, file in enumerate(files):
            AdFile.objects.create(ad=ad, file=file, order=ad.files.count() + idx)

        messages.success(self.request, MSG_SUCCESS_CREATE)
        return redirect('board:ad_detail', pk=ad.pk)

    def form_invalid(self, form):
        messages.error(self.request, MSG_ERROR_CREATE)
        return super().form_invalid(form)


class AdUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ad
    form_class = AdForm
    template_name = 'board/ad_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = UPDATE_TITLE
        context['button_text'] = UPDATE_BUTTON_TEXT
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
            messages.error(self.request, MSG_ERROR_IMAGE)
            return redirect('board:ad_update', pk=ad.pk)

        total_files = existing_files_count + len(new_files)
        if total_files > 4:
            messages.error(self.request, MSG_ERROR_FILE)
            return redirect('board:ad_update', pk=ad.pk)

        for idx, img in enumerate(new_images):
            AdImage.objects.create(ad=ad, image=img, order=existing_images_count + idx)

        for idx, file in enumerate(new_files):
            AdFile.objects.create(ad=ad, file=file, order=existing_files_count + idx)

        messages.success(self.request, MSG_SUCCESS_UPDATE)
        return redirect('board:ad_detail', pk=ad.pk)

    def form_invalid(self, form):
        messages.error(self.request, MSG_ERROR_UPDATE)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('board:ad_detail', kwargs={'pk': self.object.pk})


class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ad
    template_name = 'board/ad_confirm_delete.html'
    success_url = reverse_lazy('board:ad_list')

    def test_func(self):
        ad = self.get_object()
        return self.request.user.is_staff or ad.author == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, MSG_SUCCESS_DELETE)
        return super().delete(request, *args, **kwargs)


class CategoryAdListView(ListView):
    model = Ad
    template_name = 'board/category_ads.html'
    context_object_name = 'ads'
    paginate_by = PAGE_SIZE

    def get_queryset(self):
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
        context['title'] = CATEGORY_LIST_TITLE.format(category=self.category.name)
        return context


class SearchAdListView(ListView):
    model = Ad
    template_name = 'board/search_results.html'
    context_object_name = 'ads'
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        queryset = Ad.objects.filter(
            is_active=True, published_until__gt=timezone.now()
        ).select_related('category', 'author')

        self.query = self.request.GET.get('q', '')
        self.category_id = self.request.GET.get('category', '')
        self.city = self.request.GET.get('city', '')
        self.ad_type = self.request.GET.get('ad_type', '')

        if self.query:
            queryset = queryset.filter(
                Q(title__iregex=self.query) | Q(description__iregex=self.query)
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
        context['title'] = f'Поиск: {self.query}' if self.query else 'Поиск объявлений'
        return context


class DeleteImageView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            image = get_object_or_404(AdImage, pk=pk)
            ad = image.ad

            if request.user != ad.author and not request.user.is_staff:
                return JsonResponse(
                    {'success': False, 'error': MSG_PERMISSION_DENIED},
                    status=HTTPStatus.FORBIDDEN,
                )

            file_path = image.image.name
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            image.delete()

            return JsonResponse(
                {'success': True, 'message': MSG_SUCCESS_IMAGE}, status=HTTPStatus.OK
            )

        except Exception as e:
            return JsonResponse(
                {'success': False, 'error': str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR
            )


class DeleteFileView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            file_obj = get_object_or_404(AdFile, pk=pk)
            ad = file_obj.ad

            if request.user != ad.author and not request.user.is_staff:
                return JsonResponse(
                    {'success': False, 'error': MSG_PERMISSION_DENIED},
                    status=HTTPStatus.FORBIDDEN,
                )

            file_path = file_obj.file.name
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            file_obj.delete()

            return JsonResponse(
                {'success': True, 'message': MSG_SUCCESS_FILE}, status=HTTPStatus.OK
            )

        except Exception as e:
            return JsonResponse(
                {'success': False, 'error': str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR
            )


class AboutView(TemplateView):
    template_name = 'board/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_ads'] = Ad.objects.filter(is_active=True).count()
        context['total_categories'] = Category.objects.filter(is_active=True).count()
        context['title'] = ABOUT_TITLE
        return context
