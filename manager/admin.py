from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django.utils.translation import gettext_lazy as _
from .models import MyUser, Article, ArticleImage, Comment, Notification


class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1


@admin.register(Article)
class ArticleAdmin(TranslationAdmin):
    list_display = ('title', 'author', 'created_at', 'views')
    list_filter = ('created_at', 'author')
    readonly_fields = ('views',)
    search_fields = ('title', 'content')
    inlines = [ArticleImageInline]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        (_('O\'zbekcha ma’lumotlar'), {
            'fields': ('title_uz', 'content_uz'),
            'classes': ('collapse',),
        }),
        (_('Ruscha ma’lumotlar'), {
            'fields': ('title_ru', 'content_ru'),
            'classes': ('collapse',),
        }),
        (_('Inglizcha ma’lumotlar'), {
            'fields': ('title_en', 'content_en'),
            'classes': ('collapse',),
        }),
        (_('Asosiy ma’lumotlar'), {
            'fields': ('author',),
            'classes': ('collapse',),
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author':
            if MyUser.objects.all().exists():
                kwargs['empty_label'] = _("Tanlang")
            else:
                kwargs['empty_label'] = _("Mavjud emas")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_verified', 'is_staff')
    list_filter = ('is_verified', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    readonly_fields = ('last_login', 'date_joined')
    fieldsets = (
        (_('Foydalanuvchi maʼlumotlari'), {
            'fields': ('first_name', 'last_name', 'username', 'email', 'password', 'telegram_id', 'avatar', 'is_verified')
        }),
        (_('Ruxsatlar'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Tizim maʼlumotlari'), {
            'fields': ('last_login', 'date_joined')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('content', 'user__username', 'article__title')
    ordering = ['-created_at']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            if MyUser.objects.exists():
                kwargs['empty_label'] = _("Tanlang")
            else:
                kwargs['empty_label'] = _("Mavjud emas")

        elif db_field.name == 'article':
            if Article.objects.exists():
                kwargs['empty_label'] = _("Tanlang")
            else:
                kwargs['empty_label'] = _("Mavjud emas")

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['message', 'user__username']
