from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("payments", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="paymenttransaction",
            name="order_status",
            field=models.CharField(
                choices=[
                    ("awaiting_confirmation", "در انتظار تأیید"),
                    ("confirmed", "تأییدشده"),
                    ("preparing", "در حال آماده‌سازی"),
                    ("shipped", "ارسال‌شده"),
                    ("delivered", "تحویل‌شده"),
                    ("cancelled", "لغوشده"),
                ],
                default="awaiting_confirmation",
                max_length=30,
            ),
        ),
    ]
