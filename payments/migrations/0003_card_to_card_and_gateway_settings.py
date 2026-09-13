from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("payments", "0002_paymenttransaction_order_status")]

    operations = [
        migrations.AlterField(
            model_name="paymenttransaction",
            name="method",
            field=models.CharField(
                choices=[("crypto", "کریپتو"), ("zarinpal", "زرین‌پال"), ("card_to_card", "کارت به کارت")],
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name="PaymentGatewaySettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("zarinpal_enabled", models.BooleanField(default=True, verbose_name="فعال بودن زرین‌پال")),
                ("crypto_enabled", models.BooleanField(default=True, verbose_name="فعال بودن کریپتو")),
                ("card_to_card_enabled", models.BooleanField(default=True, verbose_name="فعال بودن کارت به کارت")),
                ("card_number", models.CharField(default="6219861475791009", max_length=19, verbose_name="شماره کارت مقصد")),
                ("card_holder_name", models.CharField(blank=True, max_length=120, verbose_name="نام صاحب کارت")),
            ],
            options={"verbose_name": "تنظیمات درگاه‌های پرداخت", "verbose_name_plural": "تنظیمات درگاه‌های پرداخت"},
        ),
    ]
