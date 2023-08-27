from django.shortcuts import render
from django.core.paginator import Paginator
from django.core import serializers
from info_app.filter import *

PATH = ""


# Create your views here.
def placeList(request):

    if request.method == "GET":
        q = request.GET.get('q')

        area_obj, categorys = category_filter(q)
        total_obj_cnt = len(area_obj)

        paginator = Paginator(area_obj, 15)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
         
        context = {
            "page_obj": page_obj,
            "categorys": categorys,
            "select_category" : q,
            "total_obj_cnt": total_obj_cnt,
        }
    return render(request, PATH + "infoPages/placeList.html", context)


def population(request):
    if request.method == "GET":
        area = request.GET.get('area')

        congest, congest_fcst, congest_past = population_filter(area)

        congest_json = serializers.serialize('json',congest)

        context = {
            "congest": congest[0],
            "congest_fcst" : congest_fcst,
            "congest_past" : congest_past,
            "congest_json" : congest_json,
        }
    return render(request, PATH + "infoPages/population.html", context)


def weather(request):
    return render(request, PATH + "infoPages/weather.html")


def restaurant(request):
    return render(request, PATH + "infoPages/restaurant.html")


def news(request):
    return render(request, PATH + "infoPages/news.html")
