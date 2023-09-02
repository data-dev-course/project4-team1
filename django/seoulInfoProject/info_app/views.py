from django.shortcuts import render
from django.core.paginator import Paginator
from django.conf import settings
from .view.filter import *
from .view.news import *

PATH = ""


# Create your views here.
def placeList(request):
    if request.method == "GET":
        q = request.GET.get("q", "전체보기")
        selected_option = request.GET.get("selected_option")

        area_obj, categorys = category_filter(q, selected_option)
        total_obj_cnt = len(area_obj)

        paginator = Paginator(area_obj, 15)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
            "categorys": categorys,
            "select_category": q,
            "total_obj_cnt": total_obj_cnt,
            "selected_option": selected_option,
        }
    return render(request, PATH + "infoPages/placeList.html", context)


def population(request):
    if request.method == "GET":
        area = request.GET.get('area')

        congest_data = population_filter(area)
        area_info, jongseong = get_area_info(area)
        msg = get_area_congest_msg(area_info)

        context = {
            "area_info": area_info,
            "jongseong": jongseong,
            "congest_msg": msg,
            "congest_data": congest_data,
        }
    return render(request, PATH + "infoPages/population.html", context)


def weather(request):
    if request.method == "GET":
        area = request.GET.get("area")
        area_info, jongseong = get_area_info(area)
        weather, weather_fcst = weather_filter(area)
        context = {
            "area_info": area_info,
            "jongseong": jongseong,
            "weather": weather[0],
            "weather_fcst": weather_fcst,
        }

    return render(request, PATH + "infoPages/weather.html", context)


def restaurant(request):
    if request.method == "GET":
        area = request.GET.get("area")
        area_info, jongseong = get_area_info(area)
        restaurant_info = restaurant_filter(area)

        paginator = Paginator(restaurant_info, 15)
        page_number = request.GET.get("page")
        restaurant_info = paginator.get_page(page_number)

        context = {
            "area_info": area_info,
            "jongseong": jongseong,
            "restaurant_info": restaurant_info,
        }
    return render(request, PATH + "infoPages/restaurant.html",context)



def news(request):
    if request.method == "GET":
        area = request.GET.get("area")
        area_info, jongseong = get_area_info(area)
        str_area_nm = area_info.area_nm
        data_path = getattr(settings, "DATA_DIR", None)
        news_area = news_data(str_area_nm, f"{data_path}/news")

        context = {
            "area_info": area_info,
            "jongseong": jongseong,
        }
        context.update(news_area)

    return render(request, PATH + "infoPages/news.html", context)

