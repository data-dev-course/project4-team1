from info_app.models import *
from django.core import serializers
from django.db.models import F


def category_filter(category):
    if category == None or category == "전체보기":
        category = "전체보기"
        congest_obj = Congest.objects.all()
    else:
        print(category)
        congest_obj = Congest.objects.filter(
            area_category=category
        )  # .select_related('seoul_data_image').filter(area_cd=F('seouldataimage__category'))

    category_class = ["전체보기", "고궁·문화유산", "공원", "관광특구", "발달상권", "인구밀집지역"]
    categorys = []
    for ca in category_class:
        ca_dic = {}
        ca_dic["name"] = ca

        if category == ca:
            ca_dic["focus"] = " on"
        else:
            ca_dic["focus"] = ""
        categorys.append(ca_dic)

    return congest_obj, categorys


def population_filter(area):
    congest = Congest.objects.filter(area_cd=area)
    congest_json = serializers.serialize("json", congest)

    congest_fcst = CongestFcst.objects.filter(area_cd=area)
    congest_fcst_json = serializers.serialize("json", congest_fcst)

    congest_past = CongestPast.objects.filter(area_cd=area).order_by("timestamp")
    congest_past_json = serializers.serialize("json", congest_past)

    return congest_json, congest_fcst_json, congest_past_json


def get_area_info(area):
    area = Congest.objects.get(area_cd=area)
    return area


def weather_filter(area):
    weather = Weather.objects.filter(area_cd=area)

    weather_fcst = WeatherFcst.objects.filter(area_cd=area)

    return weather, weather_fcst
  