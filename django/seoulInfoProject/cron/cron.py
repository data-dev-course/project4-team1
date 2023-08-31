from django.conf import settings
from .env import *
import os

# from pytz import timezone
from datetime import datetime

# KST = timezone("Asia/Seoul")


def download_data_news():
    import boto3

    today, time = datetime.now().strftime("%Y%m%d-%H%M%S").split("-")

    print(f"[{datetime.now().strftime('%Y%m%d-%H%M%S')}] |", "=" * 10 + "download_data_news" + "=" * 10)
    AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
    AWS_S3_REGION_NAME = "ap-northeast-2"
    DATA_DIR = getattr(settings, "DATA_DIR", "")

    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME,
    )

    s3 = session.resource("s3")
    bucket = s3.Bucket(name="de-3-1")

    FLAG = True
    area_list_news = AREA_LIST_NEWS
    for area in area_list_news:
        try:
            file_path = DATA_DIR / f"news/{area}"
            mkdir(file_path)

            file_name = f"{area}-{today}.json"  # 파일 이름
            bucket_path = f"area_news/{area}"  # 버켓 주소

            bucket.download_file(f"{bucket_path}/{file_name}", f"{file_path}/{file_name}")
        except Exception as e:
            FLAG = False
            print(f"[{datetime.now().strftime('%Y%m%d-%H%M%S')}] | 실패 장소: {area} | error message: {e}")

    if FLAG:
        print(f"[{datetime.now().strftime('%Y%m%d-%H%M%S')}] | 실패 장소 없음 ")

    print(f"[{datetime.now().strftime('%Y%m%d-%H%M%S')}] |", "=" * 30)


def mkdir(dir):
    try:
        if not os.path.exists(dir):
            os.makedirs(dir)
    except OSError:
        print(f"[{datetime.now().strftime('%Y%m%d-%H%M%S')}] | Error: Failed to create the directory.")


def rm_news():
    import subprocess

    print("=" * 10 + "rm_news" + "=" * 10)
    rm = subprocess.run(["sh", "cron/rm_news.sh"], capture_output=True, encoding="utf-8")
    if rm.stdout:
        print(rm.stdout)
    else:
        print("2일 이전의 json 파일이 없습니다.")
    print("=" * 25)
    # sudo find /var/app/current/data/news -name '*.json' -mtime +2 -delete


if __name__ == "__main__":
    download_data_news()
    # rm_news()
