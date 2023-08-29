from django.shortcuts import render
from django.core.paginator import Paginator
from django.core import serializers
from info_app.filter import *

PATH = ""


# Create your views here.
def placeList(request):
    if request.method == "GET":
        q = request.GET.get("q")

        area_obj, categorys = category_filter(q)
        total_obj_cnt = len(area_obj)

        paginator = Paginator(area_obj, 15)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
            "categorys": categorys,
            "select_category": q,
            "total_obj_cnt": total_obj_cnt,
        }
    return render(request, PATH + "infoPages/placeList.html", context)


def population(request):
    if request.method == "GET":
        area = request.GET.get("area")

        congest_json, congest_fcst_json, congest_past_json = population_filter(area)
        area_info = get_area_info(area)

        context = {
            "area_info": area_info,
            "congest_json": congest_json,
            "congest_fcst_json": congest_fcst_json,
            "congest_past_json": congest_past_json,
        }
    return render(request, PATH + "infoPages/population.html", context)


def weather(request):
    if request.method == "GET":
        area = request.GET.get("area")
        area_info = get_area_info(area)

        weather, weather_fcst = weather_filter(area)
        context = {
            "area_info": area_info,
            "weather" : weather[0],
            "weather_fcst" : weather_fcst,
        }
    return render(request, PATH + "infoPages/weather.html", context)


def restaurant(request):
    if request.method == "GET":
        area = request.GET.get("area")
        area_info = get_area_info(area)

        context = {
            "area_info": area_info,
        }
    return render(request, PATH + "infoPages/restaurant.html", context)


def news(request):
    if request.method == "GET":
        area = request.GET.get("area")
        area_info = get_area_info(area)
        context = {
            "area_info": area_info,
        }
    return render(request, PATH + "infoPages/news.html", context)
