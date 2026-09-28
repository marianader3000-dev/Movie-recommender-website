# 🎬 موقع ترشيح الأفلام (Django)

موقع ويب لترشيح الأفلام مبني بـ Django، فيه:

- عرض كل الأفلام مع فلترة بالنوع (Genre) وبحث بالاسم/المخرج
- صفحة تفاصيل لكل فيلم (وصف، مخرج، مدة، متوسط التقييم)
- تسجيل مستخدمين + تسجيل دخول/خروج
- نظام تقييم من 1 لـ 5 نجوم لكل مستخدم
- **محرّك ترشيح ذكي (Content-Based)**: بيحلل الأنواع اللي المستخدم قيّمها عالي (4 أو 5 نجوم)
  وبيرشّحله أفلام تانية بنفس الأنواع، مرتبة حسب مدى التطابق ومتوسط تقييم الفيلم.
- لوحة تحكم Admin كاملة لإدارة الأفلام والأنواع والتقييمات

## هيكل المشروع

```
movie_recommender/
├── manage.py
├── requirements.txt
├── movie_recommender/       # إعدادات المشروع (settings, urls)
├── movies/                  # التطبيق الرئيسي
│   ├── models.py            # Genre, Movie, Rating
│   ├── recommender.py       # محرك الترشيح
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   ├── urls.py
│   ├── templates/
│   └── management/commands/seed_movies.py   # بيانات تجريبية
└── static/css/style.css
```

## طريقة التشغيل

```bash
# 1. اعمل بيئة افتراضية (اختياري بس مستحسن)
python3 -m venv venv
source venv/bin/activate   # على ويندوز: venv\Scripts\activate

# 2. ثبّت المكتبات
pip install -r requirements.txt

# 3. اعمل الـ migrations
python manage.py migrate

# 4. (اختياري) أضف بيانات أفلام تجريبية
python manage.py seed_movies

# 5. اعمل حساب أدمن
python manage.py createsuperuser

# 6. شغّل السيرفر
python manage.py runserver
```

بعد كده افتح `http://127.0.0.1:8000/` في المتصفح.
لوحة التحكم موجودة على `http://127.0.0.1:8000/admin/`.

## إزاي تضيف أفلام جديدة

- من لوحة الأدمن (`/admin/`)، أو
- عدّل `movies/management/commands/seed_movies.py` وضيف أفلام في القايمة `MOVIES` بعدين شغّل
  `python manage.py seed_movies` تاني.

## إزاي شغالة خوارزمية الترشيح

الملف `movies/recommender.py` فيه الفكرة كاملة:

1. بيجمع كل الأفلام اللي المستخدم قيّمها 4 أو 5 نجوم.
2. بيحسب "نقاط اهتمام" لكل نوع (Genre) بناءً على تكراره في الأفلام دي ومجموع التقييمات.
3. بيدور على أفلام تانية (لسه المستخدم ما قيّمهاش) بنفس الأنواع، ويرتبهم حسب
   (نقاط تطابق الأنواع) + (متوسط تقييم الفيلم × وزن).
4. لو المستخدم جديد أو مفيش تقييمات كفاية، بيرجّعله أعلى الأفلام تقييمًا بشكل عام.

يمكن تطويرها لاحقًا لتبقى Collaborative Filtering حقيقي (باستخدام مكتبة زي `scikit-surprise`)
لو حبيت تاخد في الاعتبار تشابه المستخدمين مع بعض مش بس الأنواع.

## أفكار للتوسعة

- رفع بوسترات الأفلام كصور (مش روابط بس)
- صفحة "المفضلة" (Watchlist)
- تعليقات ومراجعات نصية
- API بـ Django REST Framework
- ترشيح Collaborative Filtering باستخدام مكتبات ML
