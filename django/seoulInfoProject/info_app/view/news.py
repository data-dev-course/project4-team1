from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import os
import json


def news_data(area, data_path) -> json:
    area = area_replace(area)

    time = timezone.now()
    today = time.strftime("%Y%m%d")
    json_path = f"{data_path}/{area}/{area}-{today}.json"

    if not os.path.exists(json_path):
        yesterday = (time - timedelta(days=1)).strftime("%Y%m%d")
        json_path = f"{data_path}/{area}-{yesterday}.json"

    with open(json_path, "r") as f:
        data = json.load(f)

    FLAG = False
    for i in range(data["display"]):
        if data["items"][i].get("img") == None:
            data["items"][i]["img"] = get_meta_og_image(data["items"][i]["link"])
            FLAG = True

    if FLAG:
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    return data


def area_replace(area) -> str:
    area = str(area)
    new_area = area.replace("·", " ").replace("(", " ").replace(")", "")
    return new_area


def get_meta_og_image(url):
    from bs4 import BeautifulSoup
    import requests

    try:
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        meta_og_image = soup.find("meta", property="og:image")
        if meta_og_image:
            return meta_og_image["content"]
        else:
            return "not found -> meta tag og:image "
    except Exception as e:
        print(f"get_meta_og_image | error: {e}")
        return None
