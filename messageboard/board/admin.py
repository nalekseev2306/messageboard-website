from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Ad

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий"""
    
    # Отображаемые поля в списке
    list_display = (
        'name', 'slug', 'order', 'is_active',
        'ad_count', 'created_at'
    )
    
    # Фильтры
    list_filter = (
        'is_active', 
        'created_at'
    )
    
    # Поля для поиска
    search_fields = ('name', 'description', 'slug')
    
    # Сортировка по умолчанию
    ordering = ('order', 'name')
    
    # Поля которые можно редактировать прямо в списке
    list_editable = ('order', 'is_active')
    
    # Поля-ссылки
    list_display_links = ('name', 'slug')
    
    # Количество записей на странице
    list_per_page = 20
    
    # Действия с выделенными записями
    actions = ['make_active', 'make_inactive']
    
    # Поля для чтения
    readonly_fields = ('created_at', 'updated_at', 'ad_count_display')
    
    # Группировка полей на странице редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Настройки отображения', {
            'fields': ('order', 'is_active')
        }),
        ('Статистика', {
            'fields': ('ad_count_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Автоматическое заполнение slug
    prepopulated_fields = {'slug': ('name',)}
    
    def ad_count(self, obj):
        """Количество объявлений в категории"""
        count = obj.ads.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:board_ad_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return 0
    ad_count.short_description = 'Объявлений'
    
    def ad_count_display(self, obj):
        """Отображение количества объявлений на странице редактирования"""
        count = obj.ads.filter(is_active=True).count()
        return format_html('<span style="font-size: 14px; font-weight: bold;">Всего объявлений: {}</span>', count)
    ad_count_display.short_description = 'Статистика'
    
    def make_active(self, request, queryset):
        """Активация выбранных категорий"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} категорий активировано.')
    make_active.short_description = 'Активировать выбранные категории'
    
    def make_inactive(self, request, queryset):
        """Деактивация выбранных категорий"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} категорий деактивировано.')
    make_inactive.short_description = 'Деактивировать выбранные категории'


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """Админка для объявлений"""
    
    # Отображаемые поля в списке
    list_display = (
        'id', 'title_preview', 'category', 'ad_type',
        'price_display', 'author_info', 'city',
        'is_active', 'status_badge', 'created_at'
    )
    
    # Фильтры
    list_filter = (
        'category',
        'ad_type',
        'is_active',
        'city',
        ('created_at', admin.DateFieldListFilter),
    )
    
    # Поля для поиска
    search_fields = (
        'title', 
        'description', 
        'contact_phone', 
        'contact_email',
        'city',
    )
    
    # Сортировка по умолчанию
    ordering = ('-created_at',)
    
    # Поля которые можно редактировать прямо в списке
    list_editable = ('is_active',)
    
    # Поля-ссылки
    list_display_links = ('id', 'title_preview')
    
    # Количество записей на странице
    list_per_page = 20
    
    # Действия с выделенными записями
    actions = ['make_active', 'make_inactive']
    
    # Поля для чтения
    readonly_fields = (
        'created_at', 
        'updated_at',
    )
    
    # Группировка полей на странице редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'ad_type')
        }),
        ('Цена', {
            'fields': ('price',)
        }),
        ('Контактная информация', {
            'fields': ('contact_name', 'contact_phone', 'contact_email')
        }),
        ('Локация', {
            'fields': ('city',)
        }),
        ('Изображение', {
            'fields': ('main_image',),
            'classes': ('wide',)
        }),
        ('Статусы и даты', {
            'fields': ('is_active', 'published_until', 'created_at', 'updated_at')
        }),
        ('Автор', {
            'fields': ('author',),
            'classes': ('collapse',)
        })
    )
    
    # Фильтр по дате в боковой панели
    date_hierarchy = 'created_at'
    
    # Сохраняем фильтры между сессиями
    save_as = True
    save_on_top = True
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related('category', 'author')
    
    def title_preview(self, obj):
        """Предпросмотр заголовка"""
        if len(obj.title) > 50:
            return obj.title[:47] + '...'
        return obj.title
    title_preview.short_description = 'Заголовок'
    
    def price_display(self, obj):
        """Отображение цены"""
        if obj.price is None:
            return format_html('<span style="color: gray;">Не указана</span>')
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">{} ₽</span>',
            f'{obj.price:,.0f}'.replace(',', ' ')
        )
    price_display.short_description = 'Цена'
    price_display.admin_order_field = 'price'
    
    def author_info(self, obj):
        """Информация об авторе"""
        if not obj.author:
            return format_html('<span style="color: gray;">Не указан</span>')
        
        try:
            url = reverse('admin:users_user_change', args=[obj.author.id])
            return format_html(
                '<a href="{}" style="text-decoration: none;">{}<br><span style="font-size: 0.85em; color: gray;">{}</span></a>',
                url,
                obj.author.username,
                obj.author.email or 'нет email'
            )
        except:
            return f"{obj.author.username} (email: {obj.author.email or 'нет'})"
    author_info.short_description = 'Автор'
    
    def status_badge(self, obj):
        """Статус объявления"""
        status_html = []
        
        # Статус активности
        if obj.is_active:
            status_html.append('<span style="color: green;">Активно</span>')
        else:
            status_html.append('<span style="color: red;">Неактивно</span>')
        
        if obj.is_expired:
            status_html.append('<br><span style="color: orange;">Просрочено</span>')
        
        return format_html(''.join(status_html))
    status_badge.short_description = 'Статус'
    
    def make_active(self, request, queryset):
        """Активация выбранных объявлений"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} объявлений активировано.')
    make_active.short_description = 'Активировать выбранные объявления'
    
    def make_inactive(self, request, queryset):
        """Деактивация выбранных объявлений"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} объявлений деактивировано.')
    make_inactive.short_description = 'Деактивировать выбранные объявления'
    
    def save_model(self, request, obj, form, change):
        """При сохранении устанавливаем автора, если не указан"""
        if not obj.author and request.user.is_authenticated:
            obj.author = request.user
        super().save_model(request, obj, form, change)
