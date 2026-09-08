from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "slug",
            "title",
            "excerpt",
            "category",
            "content",
            "image",
            "published_at",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def get_image(self, obj):
        request = self.context.get("request")
        url = obj.cover_url
        if url and request is not None and url.startswith("/"):
            return request.build_absolute_uri(url)
        return url

    def get_content(self, obj):
        return obj.content_paragraphs


class PostWriteSerializer(serializers.ModelSerializer):
    content = serializers.ListField(child=serializers.CharField(), allow_empty=False)

    class Meta:
        model = Post
        fields = [
            "id",
            "slug",
            "title",
            "excerpt",
            "category",
            "content",
            "image",
            "image_url",
            "published_at",
            "is_published",
        ]
        read_only_fields = ["id", "slug"]

    def validate_content(self, value):
        paragraphs = [item.strip() for item in value if item and item.strip()]
        if not paragraphs:
            raise serializers.ValidationError("محتوا نباید خالی باشد.")
        return paragraphs

    def create(self, validated_data):
        content = validated_data.pop("content", [])
        validated_data["content"] = "\n\n".join(content)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        content = validated_data.pop("content", None)
        if content is not None:
            validated_data["content"] = "\n\n".join(content)
        return super().update(instance, validated_data)
