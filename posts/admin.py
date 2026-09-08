from django.contrib import admin
from django.utils.html import format_html

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("thumb", "title", "category", "published_at", "is_published", "updated_at")
    list_display_links = ("thumb", "title")
    list_filter = ("category", "is_published", "published_at")
    list_editable = ("is_published",)
    search_fields = ("title", "excerpt", "content", "slug")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("title", "slug", "category", "published_at", "is_published")}),
        ("خلاصه و محتوا", {"fields": ("excerpt", "content")}),
        ("تصویر", {"fields": ("image", "image_url")}),
        ("تاریخ‌ها", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="تصویر")
    def thumb(self, obj):
        url = obj.cover_url
        if not url:
            return "—"
        return format_html('<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px" />', url)

