from django.contrib import admin
from .models import Genre, Movie, Rating


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["title", "release_year", "director", "average_rating", "rating_count"]
    list_filter = ["genres", "release_year"]
    search_fields = ["title", "director", "description"]
    filter_horizontal = ["genres"]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["user", "movie", "score", "created_at"]
    list_filter = ["score"]
