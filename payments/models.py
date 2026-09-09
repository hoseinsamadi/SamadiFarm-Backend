from django.conf import settings
from django.db import models


class PaymentTransaction(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        PAID = "paid", "موفق"
        FAILED = "failed", "ناموفق"
        REFUNDED = "refunded", "برگشت داده‌شده"

    class Method(models.TextChoices):
        CRYPTO = "crypto", "کریپتو"
        ZARINPAL = "zarinpal", "زرین‌پال"

    class OrderStatus(models.TextChoices):
        AWAITING_CONFIRMATION = "awaiting_confirmation", "در انتظار تأیید"
        CONFIRMED = "confirmed", "تأییدشده"
        PREPARING = "preparing", "در حال آماده‌سازی"
        SHIPPED = "shipped", "ارسال‌شده"
        DELIVERED = "delivered", "تحویل‌شده"
        CANCELLED = "cancelled", "لغوشده"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="payment_transactions")
    customer_name = models.CharField(max_length=180, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=30, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=12, default="IRT")
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    order_status = models.CharField(max_length=30, choices=OrderStatus.choices, default=OrderStatus.AWAITING_CONFIRMATION)
    authority = models.CharField(max_length=180, blank=True)
    transaction_hash = models.CharField(max_length=180, blank=True, help_text="هش تراکنش بلاکچین یا شناسه پیگیری درگاه")
    network = models.CharField(max_length=50, blank=True)
    wallet_address = models.CharField(max_length=80, blank=True)
    items = models.JSONField(default=list, blank=True)
    shipping_address = models.JSONField(default=dict, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "تراکنش پرداخت"
        verbose_name_plural = "تراکنش‌های پرداخت"

    def __str__(self):
        return f"#{self.pk} - {self.customer_name or self.customer_email or 'کاربر مهمان'} - {self.amount} {self.currency}"
