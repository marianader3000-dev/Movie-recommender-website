from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RatingForm
from .models import Genre, Movie, Rating
from .recommender import get_recommendations_for_user, get_similar_movies


def home(request):
    genre_id = request.GET.get("genre")
    query = request.GET.get("q")

    movies = Movie.objects.annotate(avg_rating=Avg("ratings__score")).prefetch_related("genres")

    if genre_id:
        movies = movies.filter(genres__id=genre_id)
    if query:
        movies = movies.filter(Q(title__icontains=query) | Q(director__icontains=query))

    movies = movies.distinct().order_by("-release_year")

    recommendations = get_recommendations_for_user(request.user, limit=8)

    context = {
        "movies": movies,
        "genres": Genre.objects.all(),
        "recommendations": recommendations,
        "selected_genre": int(genre_id) if genre_id else None,
        "query": query or "",
    }
    return render(request, "movies/home.html", context)


def movie_detail(request, pk):
    movie = get_object_or_404(
        Movie.objects.annotate(avg_rating=Avg("ratings__score")).prefetch_related("genres"),
        pk=pk,
    )
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(user=request.user, movie=movie).first()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "لازم تسجّل دخول علشان تقيّم فيلم.")
            return redirect("login")
        form = RatingForm(request.POST, instance=user_rating)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.movie = movie
            rating.save()
            messages.success(request, "تم حفظ تقييمك، شكرًا!")
            return redirect("movie_detail", pk=movie.pk)
    else:
        form = RatingForm(instance=user_rating)

    similar_movies = get_similar_movies(movie)

    context = {
        "movie": movie,
        "form": form,
        "user_rating": user_rating,
        "similar_movies": similar_movies,
    }
    return render(request, "movies/movie_detail.html", context)


@login_required
def recommendations_view(request):
    recommendations = get_recommendations_for_user(request.user, limit=20)
    return render(request, "movies/recommendations.html", {"recommendations": recommendations})


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "تم إنشاء حسابك بنجاح!")
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
