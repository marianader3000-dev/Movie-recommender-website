from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("movie/<int:pk>/", views.movie_detail, name="movie_detail"),
    path("recommendations/", views.recommendations_view, name="recommendations"),
    path("signup/", views.signup, name="signup"),
]
