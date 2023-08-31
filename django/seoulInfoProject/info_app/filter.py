from info_app.models import *
from django.core import serializers
from django.db.models import Max, Func


def category_filter(category, selected_option):
    if category == "전체보기":
        congest_obj = Congest.objects.all()
    else:
        print(category)
        congest_obj = Congest.objects.filter(area_category=category)

    if selected_option == "option2":
        ko_kr = Func(
            "area_nm",
            function="ko_KR.utf8",
            template='(%(expressions)s) COLLATE "%(function)s"',
        )
        congest_obj = congest_obj.order_by(ko_kr.asc())
    else:
        congest_obj = congest_obj.order_by('congest_lvl_one_hot','-area_ppltn_max')
        
    category_class = ["전체보기","고궁·문화유산","공원","관광특구","발달상권","인구밀집지역"]
    categorys = []
    for ca in category_class:
        ca_dic = {}
        ca_dic["name"] = ca
        
        if category == ca:
            ca_dic['focus'] = ' on'
        else:
            ca_dic["focus"] = ""
        categorys.append(ca_dic)
        
    return congest_obj, categorys



def population_filter(area):
    congest = Congest.objects.filter(area_cd = area)
    congest_json = serializers.serialize('json',congest)

    congest_fcst = CongestFcst.objects.filter(area_cd = area)
    congest_fcst_json = serializers.serialize('json',congest_fcst)

    congest_past = CongestPast.objects.filter(area_cd = area).order_by('timestamp')
    congest_past_json = serializers.serialize('json',congest_past)


    return congest_json, congest_fcst_json, congest_past_json

def cal_past_population(area):
    #congest = Congest.objects.get(area_cd = area)
    congest_past =CongestPast.objects.filter(area_cd = area)
    max_price = congest_past.aggregate(Max('area_ppltn_max'))['area_ppltn_max__max']
    congest_max = congest_past.filter(area_ppltn_max = max_price).first()
    return congest_max
    

def cal_past_population(area):
    # congest = Congest.objects.get(area_cd = area)
    congest_past = CongestPast.objects.filter(area_cd=area)
    max_price = congest_past.aggregate(Max("area_ppltn_max"))["area_ppltn_max__max"]
    congest_max = congest_past.filter(area_ppltn_max=max_price).first()
    return congest_max


def get_area_info(area):
    area = Congest.objects.get(area_cd=area)
    area_split = area.area_nm[-1]
    jongseong = has_jongseong(area_split)
    return area, jongseong


def get_area_congest_msg(area_info):
    msg = area_info.area_congest_msg
    msg_list = msg.split(".")

    for i in range(len(msg_list)):
        if msg_list[i] == "" or "지도" in msg_list[i]:
            msg_list.pop(i)

    return msg_list


def cal_congest(area_info):
    if area_info.male_ppltn_rate > area_info.male_ppltn_rate:
        gender = "남성"
        gender_val = round(area_info.male_ppltn_rate - area_info.female_ppltn_rate, 1)
    else:
        gender = "여자"
        gender_val = round(area_info.female_ppltn_rate - area_info.male_ppltn_rate, 1)

    age_dic = {
        "10대 이하": area_info.ppltn_rate_0 + area_info.ppltn_rate_10,
        "20대": area_info.ppltn_rate_20,
        "30대": area_info.ppltn_rate_30,
        "40대": area_info.ppltn_rate_40,
        "50대": area_info.ppltn_rate_50,
        "60대 이상": area_info.ppltn_rate_60 + area_info.ppltn_rate_70,
    }

    max_key_value = max(age_dic.items(), key=lambda x: x[1])
    age, age_val = max_key_value

    if area_info.resnt_ppltn_rate > area_info.non_resnt_ppltn_rate:
        resnt = "상주"
        resnt_val = round(
            area_info.resnt_ppltn_rate - area_info.non_resnt_ppltn_rate, 1
        )
    else:
        resnt = "비상주"
        resnt_val = round(
            area_info.non_resnt_ppltn_rate - area_info.resnt_ppltn_rate, 1
        )

    max_past_congest = cal_past_population(area_info.area_cd)

    result = {
        "gender": gender,
        "gender_val": gender_val,
        "age": age,
        "age_val": age_val,
        "resnt": resnt,
        "resnt_val": resnt_val,
        "max_past_congest": max_past_congest,
    }

    return result

    
def has_jongseong(character):
    # 한글의 유니코드 범위: 0xAC00 ~ 0xD7A3
    # 받침이 있는 경우 유니코드 코드 포인트는 0x11A7 ~ 0x11C2
    unicode_point = ord(character)
    remainder = (unicode_point - 0xAC00) % 28
    if remainder > 0:
        return "은"
    else:
        return "는"


def weather_filter(area):
    weather = Weather.objects.filter(area_cd=area)

    weather_fcst = WeatherFcst.objects.filter(area_cd=area)

    return weather, weather_fcst


def restaurant_filter(area):
    restaurant = Restaurant.objects.filter(area_cd=area)
    return restaurant
