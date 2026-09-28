from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Avg


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    release_year = models.PositiveIntegerField()
    poster_url = models.URLField(blank=True, help_text="رابط صورة البوستر (اختياري)")
    genres = models.ManyToManyField(Genre, related_name="movies")
    director = models.CharField(max_length=150, blank=True)
    duration_minutes = models.PositiveIntegerField(default=90)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-release_year", "title"]

    def __str__(self):
        return f"{self.title} ({self.release_year})"

    def get_absolute_url(self):
        return reverse("movie_detail", args=[self.pk])

    @property
    def average_rating(self):
        result = self.ratings.aggregate(avg=Avg("score"))["avg"]
        return round(result, 1) if result else None

    @property
    def rating_count(self):
        return self.ratings.count()


class Rating(models.Model):
    SCORE_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")

    def __str__(self):
        return f"{self.user.username} -> {self.movie.title}: {self.score}"
