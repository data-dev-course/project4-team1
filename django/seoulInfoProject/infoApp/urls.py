from django.contrib import admin
from django.urls import path
import infoApp.views

urlpatterns = [
    path('', infoApp.views.home),
    path("info/", infoApp.views.info, name="info")
]