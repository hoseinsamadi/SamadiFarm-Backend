from django.db import models
from django.utils import timezone


class Review(models.Model):
    name = models.CharField("نام", max_length=120)
    city = models.CharField("شهر", max_length=80, blank=True, default="ایران")
    stars = models.PositiveSmallIntegerField("امتیاز", choices=[(value, f"{value} ستاره") for value in range(1, 6)])
    text = models.TextField("متن دیدگاه", max_length=2000)
    is_approved = models.BooleanField("تأیید شده", default=False)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    approved_at = models.DateTimeField("تاریخ تأیید", blank=True, null=True)

    class Meta:
        verbose_name = "دیدگاه"
        verbose_name_plural = "دیدگاه‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.stars} ستاره"

    def save(self, *args, **kwargs):
        if self.is_approved and self.approved_at is None:
            self.approved_at = timezone.now()
        elif not self.is_approved:
            self.approved_at = None
        super().save(*args, **kwargs)
