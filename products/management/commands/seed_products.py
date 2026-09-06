from django.core.management.base import BaseCommand

from products.models import Product

SEED = [
    dict(slug="p-thyme", name="عسل آویشن دماوند", cat="single", weight="۹۰۰ گرم", price=685000,
         desc="تند و معطر؛ برداشت تیرماه از مراتع آویشن‌زار بالای روستای دشتک.",
         img_url="https://image.qwenlm.ai/generated-images/4d9944ff-6f97-40a9-8147-10e3379609c6/_result.png",
         tag="پرفروش‌ترین", tag_tone="ember", stock=40),
    dict(slug="p-wild", name="عسل چندگیاه ییلاقی", cat="multi", weight="۹۰۰ گرم", price=545000,
         desc="شهد گل‌های وحشی دشت لار؛ روشن، ملایم و همه‌پسند برای صبحانه.",
         img_url="https://image.qwenlm.ai/generated-images/17f20ccd-e2b6-44a8-9a71-4d7f10c3a88a/_result.png",
         tag="برداشت ۱۴۰۴", tag_tone="honey", stock=40),
    dict(slug="p-comb", name="شهد با موم طبیعی", cat="hive", weight="۷۵۰ گرم", price=790000,
         desc="مومِ بافته‌شده با شهدِ تازه؛ نزدیک‌ترین تجربه به چشیدن عسل از کندو.",
         img_url="https://image.qwenlm.ai/generated-images/8026c46a-c307-4be4-b9be-0f3b58460805/_result.png",
         tag="محدود", tag_tone="olive", stock=15),
    dict(slug="p-gon", name="عسل گون سبلان", cat="single", weight="۹۰۰ گرم", price=615000,
         desc="شیره‌ی روشن و کش‌دار گون‌های دامنه‌ی سبلان؛ شیرینیِ لطیف و ماندگار.",
         img_url="https://image.qwenlm.ai/generated-images/e6c3f5ca-0c50-4fb3-ba2a-8360b731ac3a/_result.png",
         stock=25),
    dict(slug="p-propolis", name="عصاره‌ی بره‌موم", cat="hive", weight="۳۰ میلی‌لیتر", price=425000,
         desc="قطره‌ی تقویت طبیعی کندو؛ خالص، بدون الکل و افزودنی.",
         img_url="https://image.qwenlm.ai/generated-images/05a4e692-8c36-4ea1-ab49-a20be5f63e35/_result.png",
         tag="ارگانیک", tag_tone="olive", stock=30),
    dict(slug="p-pollen", name="گرده‌ی گل تازه", cat="hive", weight="۲۵۰ گرم", price=365000,
         desc="دانه‌های طلایی گرده با پروتئین گیاهی؛ مکمل روزانه‌ی صبحانه.",
         img_url="https://image.qwenlm.ai/generated-images/812fc844-913e-4da0-98fd-551ff63b9fb2/_result.png",
         stock=20),
]


class Command(BaseCommand):
    help = "محصولات اولیه‌ی سایت (همان‌هایی که فعلاً در فرانت هاردکد شده‌اند) را در دیتابیس می‌سازد."

    def handle(self, *args, **options):
        created, updated = 0, 0
        for item in SEED:
            obj, was_created = Product.objects.update_or_create(
                slug=item["slug"], defaults={k: v for k, v in item.items() if k != "slug"}
            )
            created += was_created
            updated += not was_created
        self.stdout.write(self.style.SUCCESS(f"✅ {created} محصول ساخته شد، {updated} محصول به‌روزرسانی شد."))
