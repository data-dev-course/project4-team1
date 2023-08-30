import xmltodict
import pandas as pd
import datetime
from datetime import datetime
import logging
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import Variable
from pytz import timezone
import aiohttp
import asyncio


async def get_data(area_nm, base_url, max_retries=5):
    url = f"{base_url}{area_nm}"
    data = None

    for retry in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        data = xmltodict.parse(await response.text())
                        logging.info("데이터 가져오기 성공")
                        break
                    else:
                        print("요청이 실패했습니다. 상태 코드:", response.status)
        except asyncio.TimeoutError:
            print(f"요청 시간이 초과되었습니다. {retry+1}번째 재시도 중...")

    return data


async def congest_data(data, area_nm, current_date, timestamp, category):
    live_data1 = data["SeoulRtd.citydata"]["CITYDATA"]
    live_data2 = data["SeoulRtd.citydata"]["CITYDATA"]["LIVE_PPLTN_STTS"][
        "LIVE_PPLTN_STTS"
    ]
    keys_to_extract1 = ["AREA_NM", "AREA_CD"]
    keys_to_extract2 = [
        "AREA_CONGEST_LVL",
        "AREA_CONGEST_MSG",
        "AREA_PPLTN_MIN",
        "AREA_PPLTN_MAX",
        "MALE_PPLTN_RATE",
        "FEMALE_PPLTN_RATE",
        "PPLTN_RATE_0",
        "PPLTN_RATE_10",
        "PPLTN_RATE_20",
        "PPLTN_RATE_30",
        "PPLTN_RATE_40",
        "PPLTN_RATE_50",
        "PPLTN_RATE_60",
        "PPLTN_RATE_70",
        "RESNT_PPLTN_RATE",
        "NON_RESNT_PPLTN_RATE",
        "REPLACE_YN",
    ]
    extracted_data = {key: live_data1.get(key, None) for key in keys_to_extract1}
    extracted_data.update({key: live_data2.get(key, None) for key in keys_to_extract2})
    extracted_data["TIMESTAMP"] = timestamp
    extracted_data["AREA_CATEGORY"] = category
    df = (
        pd.DataFrame([extracted_data])
        if any(extracted_data.values())
        else pd.DataFrame([None])
    )
    s3_key = f"area_data/{area_nm}/{current_date}/area_data-{area_nm}-congest_data_{current_date}.csv"
    logging.info("congest data success")
    await upload_to_s3(df, s3_key)
    return


async def congest_fcst_data(data, area_nm, current_date, timestamp):
    data1 = data["SeoulRtd.citydata"]["CITYDATA"]
    keys_to_extract1 = ["AREA_NM", "AREA_CD"]
    extracted_data = {key: data1.get(key, None) for key in keys_to_extract1}
    extracted_data["TIMESTAMP"] = timestamp
    df1 = pd.DataFrame([extracted_data])

    try:
        data2 = data["SeoulRtd.citydata"]["CITYDATA"]["LIVE_PPLTN_STTS"][
            "LIVE_PPLTN_STTS"
        ]["FCST_PPLTN"]["FCST_PPLTN"]
        df2 = pd.DataFrame(data2)

    except KeyError:
        df2 = pd.DataFrame([None])

    df1_expanded = pd.concat([df1] * len(df2), ignore_index=True)
    combined_df = pd.concat([df1_expanded, df2], axis=1)

    s3_key = f"area_data/{area_nm}/{current_date}/area_data-{area_nm}-congest_fcst_data_{current_date}.csv"
    logging.info("congest fcst data success")
    await upload_to_s3(combined_df, s3_key)
    return


async def weather_data(data, area_nm, current_date, timestamp):
    live_data1 = data["SeoulRtd.citydata"]["CITYDATA"]
    live_data2 = data["SeoulRtd.citydata"]["CITYDATA"]["WEATHER_STTS"]["WEATHER_STTS"]
    keys_to_extract1 = ["AREA_NM", "AREA_CD"]
    keys_to_extract2 = [
        "WEATHER_TIME",
        "TEMP",
        "SENSIBLE_TEMP",
        "MAX_TEMP",
        "MIN_TEMP",
        "HUMIDITY",
        "WIND_DIRCT",
        "WIND_SPD",
        "PRECIPITATION",
        "PRECPT_TYPE",
        "PCP_MSG",
        "SUNRISE",
        "SUNSET",
        "UV_INDEX_LVL",
        "UV_INDEX",
        "UV_MSG",
        "PM25_INDEX",
        "PM25",
        "PM10_INDEX",
        "PM10" "AIR_IDX",
        "AIR_IDX_MVL",
        "AIR_IDX_MAIN",
        "AIR_MSG",
    ]
    extracted_data = {key: live_data1.get(key, None) for key in keys_to_extract1}
    extracted_data.update({key: live_data2.get(key, None) for key in keys_to_extract2})
    extracted_data["TIMESTAMP"] = timestamp
    df = (
        pd.DataFrame([extracted_data])
        if any(extracted_data.values())
        else pd.DataFrame([None])
    )
    df = df.reset_index(drop=True)
    s3_key = f"area_data/{area_nm}/{current_date}/area_data-{area_nm}-weather_data_{current_date}.csv"
    logging.info("weather data success")
    await upload_to_s3(df, s3_key)
    return


async def weather_fcst_data(data, area_nm, current_date, timestamp):
    data1 = data["SeoulRtd.citydata"]["CITYDATA"]
    keys_to_extract1 = ["AREA_NM", "AREA_CD"]
    extracted_data = {key: data1.get(key, None) for key in keys_to_extract1}
    extracted_data["TIMESTAMP"] = timestamp
    df1 = pd.DataFrame([extracted_data])

    try:
        data2 = data["SeoulRtd.citydata"]["CITYDATA"]["WEATHER_STTS"]["WEATHER_STTS"][
            "FCST24HOURS"
        ]["FCST24HOURS"]
        df2 = pd.DataFrame(data2)
        df2["FCST_DT"] = df2["FCST_DT"].apply(
            lambda x: pd.to_datetime(str(x), format="%Y%m%d%H%M").strftime(
                "%Y-%m-%d %H:%M"
            )
        )

        df2["PRECIPITATION"] = df2["PRECIPITATION"].replace("-", 0)
    except KeyError:
        df2 = pd.DataFrame([None])

    df1_expanded = pd.concat([df1] * len(df2), ignore_index=True)
    combined_df = pd.concat([df1_expanded, df2], axis=1)
    s3_key = f"area_data/{area_nm}/{current_date}/area_data-{area_nm}-weather_fcst_data_{current_date}.csv"
    logging.info("weather fcst data success")
    await upload_to_s3(combined_df, s3_key)
    return


async def weather_newslist_data(data, area_nm, current_date):
    data1 = data["SeoulRtd.citydata"]["CITYDATA"]
    keys_to_extract1 = ["AREA_NM", "AREA_CD"]
    extracted_data = {key: data1.get(key, None) for key in keys_to_extract1}
    df1 = pd.DataFrame([extracted_data])

    try:
        data2 = data1.get("WEATHER_STTS", {}).get("WEATHER_STTS", {}).get("NEWS_LIST")
        if data2:
            if data2 == "None":
                return
            if isinstance(data2, dict):
                data2 = [data2]
            df2 = pd.DataFrame(data2)
        else:
            columns = ['WARN_VAL', 'WARN_STRESS', 'ANNOUNCE_TIME', 'COMMAND', 'CANCEL_YN', 'WARN_MSG']
            none_data = {col: ['정보없음'] for col in columns}
            df2 = pd.DataFrame(none_data)

    except KeyError:
        df2 = pd.DataFrame([None])

    df1_expanded = pd.concat([df1] * len(df2), ignore_index=True)
    combined_df = pd.concat([df1_expanded, df2], axis=1)

    s3_key = f"area_data/{area_nm}/{current_date}/area_data-{area_nm}-weather_newslist_data_{current_date}.csv"
    logging.info("weather newslist data success")
    await upload_to_s3(combined_df, s3_key)
    return


async def upload_to_s3(df, s3_key):
    s3_hook = S3Hook(aws_conn_id="s3_conn_id")
    logging.info("Saving {} to {} in S3".format(df, s3_key))

    await asyncio.to_thread(
        s3_hook.load_string,
        string_data=df.to_csv(index=False),
        key=s3_key,
        bucket_name=Variable.get("s3_bucket_name"),
        replace=True,
    )


async def run(area_list, base_url, area_category):
    kst = timezone("Asia/Seoul")
    current_date = datetime.now().astimezone(kst).strftime("%Y%m%d")
    timestamp = datetime.now(kst).strftime("%Y-%m-%d %H:%M")

    tasks = []
    for area_nm, category in zip(area_list, area_category):
        tasks.append(
            concurrent_task(area_nm, base_url, current_date, timestamp, category)
        )

    await asyncio.gather(*tasks)


async def concurrent_task(area_nm, base_url, current_date, timestamp, category):
    data = await get_data(area_nm, base_url)
    if data is None:
        logging.warning("Data is None. Data cannot be processed.")
        none_data_area_list.append(area_nm)
        return

    tasks = [
        congest_data(data, area_nm, current_date, timestamp, category),
        congest_fcst_data(data, area_nm, current_date, timestamp),
        weather_data(data, area_nm, current_date, timestamp),
        weather_fcst_data(data, area_nm, current_date, timestamp),
        weather_newslist_data(data, area_nm, current_date),
    ]

    await asyncio.gather(*tasks)


def run_sync(area_list, base_url, area_category):
    asyncio.run(run(area_list, base_url, area_category))
    logging.info("Done")
    if none_data_area_list:
        logging.info("Areas with None data: %s", ", ".join(none_data_area_list))
    else:
        logging.info(
            "There is no areas with None data. All data has been saved successfully."
        )


none_data_area_list = []
