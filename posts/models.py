from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class PostCategory(models.TextChoices):
    GUIDE = "guide", "راهنمای خرید"
    BEEKEEPING = "beekeeping", "عسل و زنبورداری"
    EDUCATION = "education", "آموزش زنبورداری"
    NEWS = "news", "اخبار و یادداشت"


class Post(models.Model):
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    title = models.CharField("عنوان", max_length=200)
    excerpt = models.CharField("خلاصه", max_length=320)
    category = models.CharField("دسته‌بندی", max_length=20, choices=PostCategory.choices, default=PostCategory.GUIDE)
    content = models.TextField("محتوا", help_text="هر پاراگراف را با یک خط خالی جدا کنید.")
    image = models.ImageField("تصویر", upload_to="posts/", blank=True, null=True)
    image_url = models.URLField("لینک تصویر (اختیاری)", blank=True)
    published_at = models.DateField("تاریخ انتشار", default=timezone.localdate)
    is_published = models.BooleanField("منتشر شده", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "پست"
        verbose_name_plural = "پست‌ها"
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True) or "post"
            slug = base_slug
            i = 1
            while Post.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                i += 1
                slug = f"{base_slug}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def content_paragraphs(self):
        return [line.strip() for line in self.content.split("\n\n") if line.strip()]

    @property
    def cover_url(self):
        if self.image_url:
            return self.image_url
        if self.image:
            return self.image.url
        return ""
