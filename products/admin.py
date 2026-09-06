from django.contrib import admin
from django.utils.html import format_html

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumb", "name", "cat", "price", "stock", "is_active", "updated_at")
    list_display_links = ("thumb", "name")
    list_filter = ("cat", "is_active", "tag_tone")
    list_editable = ("stock", "is_active")
    search_fields = ("name", "desc", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("name", "slug", "cat", "price", "weight", "stock", "is_active")}),
        ("توضیحات", {"fields": ("desc", "long_description", "highlights")}),
        ("تصویر و برچسب", {"fields": ("img", "img_url", "tag", "tag_tone")}),
        ("تاریخ‌ها", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="تصویر")
    def thumb(self, obj):
        url = obj.image_url
        if not url:
            return "—"
        return format_html('<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px" />', url)
