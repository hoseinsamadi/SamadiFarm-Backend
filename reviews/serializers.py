from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "name", "city", "stars", "text", "is_approved", "created_at", "approved_at"]
        read_only_fields = ["id", "is_approved", "created_at", "approved_at"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("نام باید حداقل ۲ حرف باشد.")
        return value

    def validate_text(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("دیدگاه باید حداقل ۱۰ حرف باشد.")
        return value

    def validate_city(self, value):
        return value.strip() or "ایران"
