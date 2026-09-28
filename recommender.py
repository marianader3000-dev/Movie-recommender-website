"""
محرّك ترشيح بسيط (Content-Based) يعتمد على:
1. الأنواع (Genres) اللي المستخدم قيّمها بتقييم عالي (4 أو 5).
2. متوسط تقييم الفيلم نفسه من كل المستخدمين (كعامل ترجيح إضافي).

الفكرة:
- بنجيب كل الأفلام اللي المستخدم قيّمها 4 أو أكثر.
- بنجمع الأنواع بتاعتهم ونحسب "نقاط اهتمام" لكل نوع.
- بنرشّح أفلام تانية (لسه المستخدم ما قيّمهاش) اللي بتشترك في نفس الأنواع دي،
  وبنرتبهم حسب (عدد الأنواع المشتركة * وزن الاهتمام) + متوسط تقييم الفيلم.
"""
from collections import Counter
from django.db.models import Avg, Q
from .models import Movie, Rating


def get_recommendations_for_user(user, limit=10):
    if not user or not user.is_authenticated:
        return get_top_rated_movies(limit=limit)

    liked_ratings = (
        Rating.objects.filter(user=user, score__gte=4)
        .select_related("movie")
        .prefetch_related("movie__genres")
    )

    rated_movie_ids = Rating.objects.filter(user=user).values_list("movie_id", flat=True)

    if not liked_ratings.exists():
        # مفيش تاريخ تقييمات كفاية -> رجّع الأعلى تقييمًا بشكل عام
        return get_top_rated_movies(exclude_ids=rated_movie_ids, limit=limit)

    genre_weight = Counter()
    for rating in liked_ratings:
        for genre in rating.movie.genres.all():
            genre_weight[genre.id] += rating.score

    candidate_movies = (
        Movie.objects.exclude(id__in=rated_movie_ids)
        .filter(genres__id__in=genre_weight.keys())
        .distinct()
        .prefetch_related("genres")
        .annotate(avg_rating=Avg("ratings__score"))
    )

    scored = []
    for movie in candidate_movies:
        genre_score = sum(genre_weight.get(g.id, 0) for g in movie.genres.all())
        rating_bonus = (movie.avg_rating or 0) * 2
        total_score = genre_score + rating_bonus
        scored.append((total_score, movie))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    recommended = [movie for _, movie in scored[:limit]]

    if len(recommended) < limit:
        # كمّل بأفلام عالية التقييم في حالة مفيش ترشيحات كفاية
        fallback = get_top_rated_movies(
            exclude_ids=list(rated_movie_ids) + [m.id for m in recommended],
            limit=limit - len(recommended),
        )
        recommended.extend(fallback)

    return recommended


def get_top_rated_movies(exclude_ids=None, limit=10):
    qs = Movie.objects.annotate(avg_rating=Avg("ratings__score"))
    if exclude_ids:
        qs = qs.exclude(id__in=exclude_ids)
    return list(qs.order_by("-avg_rating", "-release_year")[:limit])


def get_similar_movies(movie, limit=6):
    """أفلام مشابهة لفيلم معيّن بناءً على الأنواع المشتركة."""
    genre_ids = movie.genres.values_list("id", flat=True)
    similar = (
        Movie.objects.filter(genres__id__in=genre_ids)
        .exclude(id=movie.id)
        .distinct()
        .annotate(avg_rating=Avg("ratings__score"))
        .order_by("-avg_rating")[:limit]
    )
    return list(similar)
