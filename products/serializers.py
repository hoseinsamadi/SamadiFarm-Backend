from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()
    highlights = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "name",
            "cat",
            "weight",
            "price",
            "desc",
            "long_description",
            "img",
            "tag",
            "tag_tone",
            "highlights",
            "stock",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def get_img(self, obj):
        request = self.context.get("request")
        url = obj.image_url
        if url and request is not None and url.startswith("/"):
            return request.build_absolute_uri(url)
        return url

    def get_highlights(self, obj):
        return obj.highlights_list


class ProductWriteSerializer(serializers.ModelSerializer):
    """سریالایزر جداگانه برای ساخت/ویرایش محصول از طریق API (آپلود تصویر مستقیم)."""

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "name",
            "cat",
            "weight",
            "price",
            "desc",
            "long_description",
            "img",
            "img_url",
            "tag",
            "tag_tone",
            "highlights",
            "stock",
            "is_active",
        ]
        read_only_fields = ["id", "slug"]
