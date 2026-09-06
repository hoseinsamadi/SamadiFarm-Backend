from rest_framework import viewsets, permissions, filters

from .models import Product
from .serializers import ProductSerializer, ProductWriteSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    - GET  /api/products/          -> لیست محصولات فعال (عمومی)
    - GET  /api/products/{slug}/   -> جزئیات یک محصول (عمومی)
    - POST /api/products/          -> افزودن محصول (نیاز به لاگین ادمین/staff)
    - PATCH/PUT /api/products/{slug}/ -> ویرایش محصول (نیاز به لاگین)
    - DELETE /api/products/{slug}/ -> حذف محصول (نیاز به لاگین)
    """

    queryset = Product.objects.all().order_by("-created_at")
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "desc"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method == "GET" and not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        cat = self.request.query_params.get("cat")
        if cat:
            qs = qs.filter(cat=cat)
        return qs

    def get_serializer_class(self):
        if self.request.method in ("POST", "PUT", "PATCH"):
            return ProductWriteSerializer
        return ProductSerializer
