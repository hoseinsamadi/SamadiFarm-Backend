# Samadi Farm Backend (Django + DRF + SQLite)

بک‌اند فروشگاه صمدی فارم — قدم اول: مدیریت محصولات (افزودن/حذف/ویرایش) با پایگاه‌داده‌ی SQLite.

## اجرا روی سیستم خودتان

```bash
python -m venv venv
source venv/bin/activate      # ویندوز: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # و در صورت نیاز مقادیر را عوض کنید

python manage.py migrate
python manage.py createsuperuser
python manage.py seed_products   # اختیاری: پر کردن دیتابیس با ۶ محصول نمونه‌ی فعلی سایت
python manage.py runserver
```

سرور روی `http://127.0.0.1:8000` بالا می‌آید.

## افزودن / حذف محصول

### روش ۱ — پنل ادمین (ساده‌ترین راه)
آدرس `http://127.0.0.1:8000/admin/` را باز کنید، با کاربر سوپریوزری که ساختید وارد شوید،
از بخش «محصولات فروشگاه» می‌توانید محصول اضافه، ویرایش یا حذف کنید (شامل آپلود مستقیم عکس).

### روش ۲ — API (برای وصل‌کردن به فرانت Next.js)
| عملیات | متد | آدرس |
|---|---|---|
| لیست محصولات فعال | GET | `/api/products/` |
| فیلتر بر اساس دسته | GET | `/api/products/?cat=single` |
| جستجو | GET | `/api/products/?search=آویشن` |
| جزئیات یک محصول | GET | `/api/products/{slug}/` |
| افزودن محصول (نیاز به لاگین) | POST | `/api/products/` |
| ویرایش محصول (نیاز به لاگین) | PATCH | `/api/products/{slug}/` |
| حذف محصول (نیاز به لاگین) | DELETE | `/api/products/{slug}/` |

برای درخواست‌های POST/PATCH/DELETE باید با کاربر staff/ادمین لاگین کرده باشید
(فعلاً از طریق سشن ادمین جنگو؛ در قدم بعدی می‌توانیم احراز هویت توکنی/JWT هم اضافه کنیم
تا با صفحه‌ی `/login` فرانت هماهنگ شود).

## ساختار پروژه

```
config/       تنظیمات اصلی جنگو (settings, urls)
products/     اپ محصولات: model, admin, serializers, views, urls
manage.py
requirements.txt
```

## قدم‌های بعدی (پیشنهادی)
1. اتصال واقعی فرانت Next.js به این API به‌جای دیتای هاردکد در `src/data/site.ts`
2. احراز هویت (OTP / گوگل) مطابق چیزی که در `pages/login.tsx` پیش‌بینی شده
3. اتصال درگاه پرداخت (زرین‌پال / کریپتو) طبق `pages/checkout.tsx`
4. مدل سفارش (Order) و اتصال به حساب کاربری (`pages/account.tsx`)
5. آماده‌سازی برای دیپلوی (Postgres در production، تنظیم `DEBUG=False`، `ALLOWED_HOSTS`)
