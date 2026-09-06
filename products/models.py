from django.db import models
from django.utils.text import slugify


class Category(models.TextChoices):
    SINGLE = "single", "تک‌گل"
    MULTI = "multi", "چندگیاه"
    HIVE = "hive", "فرآورده‌های کندو"


class TagTone(models.TextChoices):
    HONEY = "honey", "عسلی"
    OLIVE = "olive", "زیتونی"
    EMBER = "ember", "اخگری"


class Product(models.Model):
    # slug همان نقشی را دارد که در فرانت روی id (مثل p-thyme) استفاده می‌شود
    # و در آدرس /products/[slug] به کار می‌رود.
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    name = models.CharField("نام محصول", max_length=150)
    cat = models.CharField("دسته‌بندی", max_length=10, choices=Category.choices, default=Category.SINGLE)
    weight = models.CharField("وزن / حجم", max_length=40, help_text="مثلاً «۹۰۰ گرم»")
    price = models.PositiveIntegerField("قیمت (تومان)")
    desc = models.TextField("توضیح کوتاه", max_length=300)
    long_description = models.TextField("توضیح کامل", blank=True)
    img = models.ImageField("تصویر محصول", upload_to="products/", blank=True, null=True)
    img_url = models.URLField("لینک تصویر (اختیاری)", blank=True, help_text="اگر پر شود، به‌جای فایل آپلودی استفاده می‌شود.")
    tag = models.CharField("برچسب", max_length=40, blank=True)
    tag_tone = models.CharField("رنگ برچسب", max_length=10, choices=TagTone.choices, blank=True)
    highlights = models.TextField(
        "ویژگی‌ها (هر خط یک مورد)", blank=True,
        help_text="هر خط یک ویژگی برای نمایش در صفحه محصول",
    )
    is_active = models.BooleanField("فعال / قابل نمایش", default=True)
    stock = models.PositiveIntegerField("موجودی", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True) or "product"
            slug = base_slug
            i = 1
            while Product.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                i += 1
                slug = f"{base_slug}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def highlights_list(self):
        return [line.strip() for line in self.highlights.splitlines() if line.strip()]

    @property
    def image_url(self):
        if self.img_url:
            return self.img_url
        if self.img:
            return self.img.url
        return ""
