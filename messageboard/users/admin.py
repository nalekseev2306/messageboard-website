from board.models import Ad
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import UserChangeForm, UserCreationForm
from users.models import User


class UserAdsInline(admin.TabularInline):
    model = Ad
    fields = ('title', 'price', 'category', 'created_at', 'is_active')
    readonly_fields = ('title', 'price', 'category', 'created_at', 'is_active')
    can_delete = False
    extra = 0
    max_num = 10
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        'username',
        'email',
        'phone',
        'city',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'ads_count',
        'date_joined',
    )

    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'city',
        'date_joined',
    )

    search_fields = (
        'username',
        'email',
        'phone',
        'first_name',
        'last_name',
        'city',
    )

    ordering = ('-date_joined',)
    list_per_page = 10

    actions = ['make_active', 'make_inactive']

    list_display_links = ('username', 'email')
    list_editable = ('is_active', 'city')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            ('Персональная информация'),
            {'fields': ('first_name', 'last_name', 'email', 'phone', 'city')},
        ),
        (
            ('Права доступа'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            ('Важные даты'),
            {'fields': ('last_login', 'date_joined'), 'classes': ('collapse',)},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'phone',
                    'city',
                    'first_name',
                    'last_name',
                    'password1',
                    'password2',
                ),
            },
        ),
    )

    inlines = [UserAdsInline]
    readonly_fields = ('date_joined', 'last_login')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('ads')

    def ads_count(self, obj):
        count = obj.ads.count()
        return f'{count}'

    ads_count.short_description = 'Объявления'
    ads_count.allow_tags = True
    ads_count.admin_order_field = 'ads__count'

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} пользователей активировано.')

    make_active.short_description = 'Активировать выбранных пользователей'

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} пользователей деактивировано.')

    make_inactive.short_description = 'Деактивировать выбранных пользователей'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(form.cleaned_data['password1'])
        super().save_model(request, obj, form, change)
