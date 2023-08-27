from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from airflow.exceptions import AirflowException, AirflowSkipException
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from pytz import timezone
from datetime import datetime
import asyncio
import json
import aiohttp
import time
import boto3
import re

# v1

KST = timezone("Asia/Seoul")

default_args = {
    'owner': 'usiohc',
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 24),
}

dag = DAG(
    'news_quarter',
    default_args=default_args,
    schedule_interval="*/15 * * * *",
    catchup=False,
)


async def fetch(client, params):
    url = "https://openapi.naver.com/v1/search/news.json"
    async with client.get(url, params=params, timeout=1) as resp:
        resp_status_code = resp.status
        assert resp.status == 200, f'status code: {resp_status_code}'
        return await resp.text()


# API 호출을 하는 Task
failed_list = []
async def call_api(place, MAX_RETRIES=5):
    for cnt in range(MAX_RETRIES):
        try:
            headers={
                "X-Naver-Client-Id": naver_client_id,
                "X-Naver-Client-Secret": naver_client_secret
            }
            params={
                'query': place, # 검색 키워드
                'display' : "10", # 한 번에 표시할 검색 결과 개수(기본값: 10, 최댓값: 100)
                # 'start' : "", # 검색 시작 위치(기본값: 1, 최댓값: 1000)
                'sort' : "date" # date (최신순), sim (정확도순)
            }
            
            async with aiohttp.ClientSession(headers=headers) as client:
                data = await fetch(client, params)
            print(f'call_api | 장소: {place} 데이터 추출 성공 ')
            
            data = json.loads(data)
            
            # api 반환시간 보기쉽게 변경
            try:
                data['lastBuildDate'] = await convert_date(data['lastBuildDate'])
                print(f'convert_date | 장소: {place} | 성공 ')
            except Exception as e:
                print(f'convert_date | 장소: {place} | 실패 | message: {e}')
            
            # title, description html 태그 제거 | 기사 발행일 보기쉽게 변경
            # Sat, 26 Aug 2023 14:36:00 +0900 -> 2023-08-26 14:36:00
            try:
                tasks = []
                for i in range(int(params['display'])):
                    tasks.append(asyncio.create_task(process_data(data['items'][i])))
                
                data['items'] = await asyncio.gather(*tasks)
                print(f'process_data | 장소: {place} | 성공 ')
            except Exception as e:
                print(f'process_data | 장소: {place} | 실패 | message: {e}')
            
            data = json.dumps(data, ensure_ascii=False, indent=4)
            today, time = datetime.now(KST).strftime("%Y%m%d-%H%M").split('-')
            filepath = f'area_news/{place}/'
            filename = f'{place}-{today}.json'
            
            try:
                await upload_to_s3(data, filepath + filename)
                print(f'upload_S3 | 장소: {place} | S3 위치: {filepath} | 파일명: {filename} | 성공')
            except Exception as e:
                print(f'upload_S3 | 장소: {place} | S3 위치: {filepath} | 파일명: {filename} | 실패')
            
            return None
        except Exception as e:
            print(f"call_api | 실패 | {cnt+1}회 시도 | 장소: {place} | message: {e}")
            await asyncio.sleep(0.5)
    else:
        failed_list.append(place)
        print(f"Warring | 장소: {place} 5회 실패")


async def process_data(data_item_idx):
    data_item_idx['title'] = await cleanhtml(data_item_idx['title'])
    data_item_idx['description'] = await cleanhtml(data_item_idx['description'])
    data_item_idx['pubDate'] = await convert_date(data_item_idx['pubDate'])
    return data_item_idx

async def convert_date(date):
    # Sat, 26 Aug 2023 14:36:00 +0900 -> 2023-08-26 14:36:00
    date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    return date


async def cleanhtml(raw_html):
    # html 태그 제거
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


s3_hook = S3Hook(aws_conn_id="s3_conn_id")
async def upload_to_s3(data_string, S3_path):
    try:
        await asyncio.to_thread(
            s3_hook.load_string,
            string_data=data_string,
            key=S3_path,
            bucket_name=Variable.get("s3_bucket_name"),
            replace=True,
        )
    except Exception as e:
        raise AirflowException(f" 실패 | message: {e}")        




def async_call_api_task():
    area_list = eval(Variable.get("area_list_news"))
    
    # 현재 실행 중인 스레드의 이벤트 루프를 가져옵니다. 만약 이벤트 루프가 없다면 새로운 이벤트 루프를 생성
    loop = asyncio.get_event_loop()

    # places를 10개씩 나누어 비동기화, naver API는 1초에 10번까지만 호출 가능
    chunk_size = 10
    total_elements = len(area_list)
    num_chunks = total_elements // chunk_size
    
    last_chunk = area_list[num_chunks * chunk_size :]
    chunks = [area_list[i * chunk_size : (i + 1) * chunk_size] for i in range(num_chunks)] + [last_chunk]
    for chunck in chunks:
        print('ㅡ'*10, chunck, 'ㅡ'*10)
        # 각각의 call_api() 호출을 리스트 컴프리헨션을 사용하여 생성
        futures = [call_api(place) for place in chunck]
        # asyncio.gather()를 사용하여 모든 Future 객체를 묶은 후, 현재 이벤트 루프를 사용하여 병렬로 실행
        # loop.run_until_complete()를 사용하여 병렬 실행이 완료될 때까지 기다립니다.
        loop.run_until_complete(asyncio.gather(*futures))
        time.sleep(0.5)

    # 이벤트 루프를 종료
    loop.close()
    
    # 실패 목록이 있으면 에러 발생
    if failed_list:
        print(f'총 place 개수:{len(area_list)} | 실패 place 개수:{len(failed_list)}')
        raise AirflowException(f"실패 목록 \n{failed_list}")


naver_client_id = Variable.get("naver_client_id")
naver_client_secret = Variable.get("naver_client_secret")
async_call_api = PythonOperator(
    task_id='async_call_api',
    python_callable=async_call_api_task,
    dag=dag,
)


async_call_api