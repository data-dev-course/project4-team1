from django.contrib import admin
from django.urls import path
import infoApp.views

urlpatterns = [
    path("", infoApp.views.placeList),
    path("population/", infoApp.views.population, name="population"),
    path("weather/", infoApp.views.weather, name="weather"),
    path("restaurant/", infoApp.views.restaurant, name="restaurant"),
    path("news/", infoApp.views.news, name="news"),
]
