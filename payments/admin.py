from django.contrib import admin
from django.db.models import Sum
from django.utils import timezone

from .models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "customer_name_label", "customer_phone_label", "amount_label", "currency_label", "method_label", "payment_status", "order_status_label", "transaction_hash_label", "created_at_label", "paid_at_label")
    list_filter = ("status", "order_status", "method", "currency", "created_at")
    search_fields = ("customer_name", "customer_email", "customer_phone", "transaction_hash", "authority")
    readonly_fields = ("user", "customer_name", "customer_email", "customer_phone", "amount", "currency", "method", "authority", "network", "wallet_address", "items", "shipping_address", "created_at")
    date_hierarchy = "created_at"
    list_per_page = 50

    @admin.display(description="شناسه")
    def transaction_id(self, obj):
        return obj.id

    @admin.display(description="نام مشتری")
    def customer_name_label(self, obj):
        return obj.customer_name or "بدون نام"

    @admin.display(description="شماره تماس")
    def customer_phone_label(self, obj):
        return obj.customer_phone or "ثبت نشده"

    @admin.display(description="مبلغ")
    def amount_label(self, obj):
        return f"{obj.amount} {obj.currency}"

    @admin.display(description="ارز")
    def currency_label(self, obj):
        return obj.currency

    @admin.display(description="روش پرداخت")
    def method_label(self, obj):
        return obj.get_method_display()

    @admin.display(description="وضعیت پرداخت")
    def payment_status(self, obj):
        return obj.get_status_display()

    @admin.display(description="وضعیت سفارش")
    def order_status_label(self, obj):
        return obj.get_order_status_display()

    @admin.display(description="هش / شناسه پیگیری")
    def transaction_hash_label(self, obj):
        return obj.transaction_hash or "ثبت نشده"

    @admin.display(description="تاریخ ثبت")
    def created_at_label(self, obj):
        return obj.created_at.strftime("%Y/%m/%d %H:%M")

    @admin.display(description="تاریخ پرداخت")
    def paid_at_label(self, obj):
        return obj.paid_at.strftime("%Y/%m/%d %H:%M") if obj.paid_at else "-"

    def save_model(self, request, obj, form, change):
        if obj.status == PaymentTransaction.Status.PAID and not obj.paid_at:
            obj.paid_at = timezone.now()
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        paid = PaymentTransaction.objects.filter(status=PaymentTransaction.Status.PAID)
        context = extra_context or {}
        context.update({"paid_total": paid.aggregate(total=Sum("amount"))["total"] or 0, "paid_count": paid.count()})
        return super().changelist_view(request, extra_context=context)
