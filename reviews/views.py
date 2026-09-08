from rest_framework import permissions, viewsets

from .models import Review
from .serializers import ReviewSerializer


class ReviewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS or request.method == "POST":
            return True
        return bool(request.user and request.user.is_staff)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [ReviewPermission]
    queryset = Review.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        return queryset

    def perform_create(self, serializer):
        serializer.save(is_approved=False)
