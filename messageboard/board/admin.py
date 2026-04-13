from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Ad, AdImage, AdFile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий"""
    
    list_display = ('name', 'slug', 'order', 'is_active', 'ad_count', 'created_at')
    list_filter = ('is_active', 'created_at',)
    search_fields = ('name', 'description', 'slug')
    ordering = ('order', 'name')
    list_editable = ('order', 'is_active',)
    list_display_links = ('name', 'slug')
    list_per_page = 20
    actions = ['make_active', 'make_inactive']
    readonly_fields = ('created_at', 'updated_at', 'ad_count_display')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description',)
        }),
        ('Настройки отображения', {
            'fields': ('order', 'is_active',)
        }),
        ('Статистика', {
            'fields': ('ad_count_display', 'created_at', 'updated_at',),
            'classes': ('collapse',)
        }),
    )
    prepopulated_fields = {'slug': ('name',)}
    
    def ad_count(self, obj):
        count = obj.ads.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:board_ad_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return 0
    ad_count.short_description = 'Объявлений'
    
    def ad_count_display(self, obj):
        count = obj.ads.filter(is_active=True).count()
        return format_html(
            '<span style="font-size: 14px; font-weight: bold;">Всего объявлений: {}</span>',
            count
        )
    ad_count_display.short_description = 'Статистика'
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} категорий активировано.')
    make_active.short_description = 'Активировать выбранные категории'
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} категорий деактивировано.')
    make_inactive.short_description = 'Деактивировать выбранные категории'


class AdImageInline(admin.TabularInline):
    """Inline для изображений объявления"""
    model = AdImage
    extra = 1
    fields = ('image_preview', 'image', 'order')
    readonly_fields = ('image_preview',)
    ordering = ('order',)
    
    def image_preview(self, obj):
        if obj and obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px; max-width: 100px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Превью'


class AdFileInline(admin.TabularInline):
    """Inline для файлов объявления"""
    model = AdFile
    extra = 1
    fields = ('file', 'file_size_display', 'order')
    readonly_fields = ('file_size_display',)
    ordering = ('order',)
    
    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size < 1024:
                return f'{obj.file_size} байт'
            elif obj.file_size < 1048576:
                return f'{obj.file_size // 1024} КБ'
            else:
                return f'{obj.file_size // 1048576} МБ'
        return '0 байт'
    file_size_display.short_description = 'Размер'


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """Админка для объявлений"""
    
    list_display = (
        'id', 'title_preview', 'category', 'ad_type', 'price_display',
        'city', 'is_active', 'status_badge', 'created_at'
    )
    list_filter = ('category', 'ad_type', 'is_active', 'city', 'created_at',)
    search_fields = ('title', 'description', 'contact_phone', 'contact_email', 'city')
    ordering = ('-created_at',)
    list_editable = ('is_active',)
    list_display_links = ('id', 'title_preview')
    list_per_page = 20
    actions = ['make_active', 'make_inactive']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'ad_type',)
        }),
        ('Цена', {
            'fields': ('price',)
        }),
        ('Контактная информация', {
            'fields': ('contact_name', 'contact_phone', 'contact_email',)
        }),
        ('Локация', {
            'fields': ('city',)
        }),
        ('Статусы и даты', {
            'fields': ('is_active', 'published_until', 'created_at', 'updated_at',)
        }),
        ('Автор', {
            'fields': ('author',),
            'classes': ('collapse',)
        }),
    )
    inlines = [AdImageInline, AdFileInline]
    date_hierarchy = 'created_at'
    save_as = True
    save_on_top = True
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'author')
    
    def title_preview(self, obj):
        if len(obj.title) > 50:
            return obj.title[:47] + '...'
        return obj.title
    title_preview.short_description = 'Заголовок'
    
    def price_display(self, obj):
        if obj.price is None:
            return format_html('<span style="color: gray;">Не указана</span>')
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">{} ₽</span>',
            f'{obj.price:,.0f}'.replace(',', ' ')
        )
    price_display.short_description = 'Цена'
    price_display.admin_order_field = 'price'
    
    def status_badge(self, obj):
        if obj.is_active:
            status = '<span style="color: green;">Активно</span>'
        else:
            status = '<span style="color: red;">Неактивно</span>'
        if obj.is_expired:
            status += '<br><span style="color: orange;">Просрочено</span>'
        return format_html(status)
    status_badge.short_description = 'Статус'
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} объявлений активировано.')
    make_active.short_description = 'Активировать выбранные объявления'
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} объявлений деактивировано.')
    make_inactive.short_description = 'Деактивировать выбранные объявления'
    
    def save_model(self, request, obj, form, change):
        if not obj.author and request.user.is_authenticated:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(AdImage)
class AdImageAdmin(admin.ModelAdmin):
    """Админка для изображений"""
    
    list_display = ('id', 'ad_link', 'image_preview', 'order', 'created_at')
    list_filter = ('created_at',)
    list_editable = ('order',)
    search_fields = ('ad__title',)
    readonly_fields = ('image_preview', 'created_at')
    fieldsets = (
        ('Изображение', {
            'fields': ('ad', 'image', 'image_preview',)
        }),
        ('Настройки', {
            'fields': ('order',)
        }),
        ('Информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def ad_link(self, obj):
        url = reverse('admin:board_ad_change', args=[obj.ad.id])
        return format_html('<a href="{}">{}</a>', url, obj.ad.title)
    ad_link.short_description = 'Объявление'
    
    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return 'Нет изображения'
    image_preview.short_description = 'Превью'


@admin.register(AdFile)
class AdFileAdmin(admin.ModelAdmin):
    """Админка для файлов"""
    
    list_display = ('id', 'ad_link', 'filename', 'file_extension', 'file_size_display', 'order', 'created_at')
    list_filter = ('created_at',)
    list_editable = ('order',)
    search_fields = ('ad__title',)
    readonly_fields = ('file_size_display', 'created_at', 'filename', 'file_extension')
    fieldsets = (
        ('Файл', {
            'fields': ('ad', 'file', 'filename',)
        }),
        ('Информация', {
            'fields': ('file_extension', 'file_size_display', 'order',)
        }),
        ('Дата', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def ad_link(self, obj):
        url = reverse('admin:board_ad_change', args=[obj.ad.id])
        return format_html('<a href="{}">{}</a>', url, obj.ad.title)
    ad_link.short_description = 'Объявление'
    
    def filename(self, obj):
        return obj.get_filename()
    filename.short_description = 'Имя файла'
    
    def file_extension(self, obj):
        return obj.file_extension.upper() if obj.file_extension else '-'
    file_extension.short_description = 'Тип'
    
    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size < 1024:
                return f'{obj.file_size} байт'
            elif obj.file_size < 1048576:
                return f'{obj.file_size // 1024} КБ'
            else:
                return f'{obj.file_size // 1048576} МБ'
        return '0 байт'
    file_size_display.short_description = 'Размер'
