from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="PaymentTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_name", models.CharField(blank=True, max_length=180)),
                ("customer_email", models.EmailField(blank=True, max_length=254)),
                ("customer_phone", models.CharField(blank=True, max_length=30)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=20)),
                ("currency", models.CharField(default="IRT", max_length=12)),
                ("method", models.CharField(choices=[("crypto", "کریپتو"), ("zarinpal", "زرین‌پال")], max_length=20)),
                ("status", models.CharField(choices=[("pending", "در انتظار بررسی"), ("paid", "موفق"), ("failed", "ناموفق"), ("refunded", "برگشت داده‌شده")], default="pending", max_length=20)),
                ("authority", models.CharField(blank=True, max_length=180)),
                ("transaction_hash", models.CharField(blank=True, help_text="هش تراکنش بلاکچین یا شناسه پیگیری درگاه", max_length=180)),
                ("network", models.CharField(blank=True, max_length=50)),
                ("wallet_address", models.CharField(blank=True, max_length=80)),
                ("items", models.JSONField(blank=True, default=list)),
                ("shipping_address", models.JSONField(blank=True, default=dict)),
                ("note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="payment_transactions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",), "verbose_name": "تراکنش پرداخت", "verbose_name_plural": "تراکنش‌های پرداخت"},
        ),
    ]
