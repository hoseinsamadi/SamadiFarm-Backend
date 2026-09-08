from rest_framework import permissions, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Post
from .serializers import PostSerializer, PostWriteSerializer


class PostPagination(PageNumberPagination):
    page_size = 10


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-published_at", "-created_at")
    lookup_field = "slug"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PostPagination

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method == "GET" and not self.request.user.is_staff:
            qs = qs.filter(is_published=True)
        return qs

    def get_serializer_class(self):
        if self.request.method in ("POST", "PUT", "PATCH"):
            return PostWriteSerializer
        return PostSerializer

