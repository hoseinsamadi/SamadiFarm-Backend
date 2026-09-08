from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "stars", "short_text", "is_approved", "created_at", "approved_at")
    list_filter = ("is_approved", "stars", "created_at")
    list_editable = ("is_approved",)
    search_fields = ("name", "city", "text")
    readonly_fields = ("created_at", "approved_at")
    ordering = ("is_approved", "-created_at")

    @admin.display(description="متن")
    def short_text(self, obj):
        return obj.text[:80] + ("..." if len(obj.text) > 80 else "")
