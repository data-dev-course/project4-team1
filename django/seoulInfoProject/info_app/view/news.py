from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import os
import json


def news_data(area, data_path):
    area = area_replace(area)

    time = timezone.now()
    today = time.strftime("%Y%m%d")
    json_path = f"{data_path}/{area}/{area}-{today}.json"

    if not os.path.exists(json_path):
        yesterday = (time - timedelta(days=1)).strftime("%Y%m%d")
        json_path = f"{data_path}/{area}-{yesterday}.json"

    with open(json_path, "r") as f:
        data = json.load(f)

    return data


def area_replace(area) -> str:
    area = str(area)
    new_area = area.replace("·", " ")
    return new_area
