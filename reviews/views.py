from django.db.models import Avg, Count
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Return rating statistics for publicly visible (approved) reviews."""
        approved_reviews = Review.objects.filter(is_approved=True)
        statistics = approved_reviews.aggregate(count=Count("id"), average=Avg("stars"))
        counts_by_stars = {
            item["stars"]: item["count"]
            for item in approved_reviews.values("stars").annotate(count=Count("id"))
        }
        total = statistics["count"]

        distribution = []
        for stars in range(5, 0, -1):
            count = counts_by_stars.get(stars, 0)
            distribution.append({
                "stars": stars,
                "count": count,
                "percentage": round((count / total) * 100, 1) if total else 0,
            })

        return Response({
            "count": total,
            "average": round(statistics["average"] or 0, 1),
            "distribution": distribution,
        })
