from info_app.models import *


def category_filter(category):
    if category == None or category == "전체보기":
        category = "전체보기"
        congest_obj = Congest.objects.all()
    else:
        print(category)
        congest_obj = Congest.objects.filter(area_category=category)

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
    congest_obj = Congest.objects.filter(area_cd=area)
    congest_fcst_obj = CongestFcst.objects.filter(area_cd=area)
    congest_past_obj = CongestPast.objects.filter(area_cd=area)

    return congest_obj, congest_fcst_obj, congest_past_obj
