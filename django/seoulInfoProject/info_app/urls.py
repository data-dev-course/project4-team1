from django.contrib import admin
from django.urls import path
import info_app.views

urlpatterns = [
    path("", info_app.views.placeList,name="placeList"),
    path("population/", info_app.views.population, name="population"),
    path("weather/", info_app.views.weather, name="weather"),
    path("restaurant/", info_app.views.restaurant, name="restaurant"),
    path("news/", info_app.views.news, name="news"),
]
