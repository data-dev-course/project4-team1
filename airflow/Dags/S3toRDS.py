from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.exceptions import AirflowException
import pandas as pd
import boto3
import io
from sqlalchemy import create_engine, Integer, Float, DateTime, Text, String
from airflow.models import Variable
from pytz import timezone

default_args = {
    "owner": "ptj",
    "depends_on_past": False,
    "start_date": datetime(2023, 8, 23),
    "retries": 1,
    "retry_delay": timedelta(seconds=1),
}

# s3 data df로 변환
def s3_to_df(data_category):
    try:
        s3_bucket = Variable.get("s3_bucket_name")
        area_list = eval(Variable.get("area_list"))
        s3_client = boto3.client("s3")

        # 현재 날짜 데이터 가져오기
        kst = timezone("Asia/Seoul")
        current_date = datetime.now().astimezone(kst).strftime("%Y%m%d")
        con_df = pd.DataFrame()

        for area in area_list:
            file_path = 'area_data/' + area +'/'+ current_date +'/'
            file_name = 'area_data-'+area+'-'+data_category+'_data_'+current_date+'.csv'
            response = s3_client.get_object(Bucket=s3_bucket, Key= file_path+file_name)

            data = response["Body"].read().decode("utf-8")
            df = pd.read_csv(io.StringIO(data))
            con_df = pd.concat([con_df,df], ignore_index=True)

    except Exception as e:
        raise AirflowException(f"s3_to_df 오류 발생. {e}")

    return (con_df)

# df를 rds에 적재
def df_to_rds(**kwargs):
    try:
        data_type = kwargs["params"]["data_type"]
        table_name = kwargs["params"]["table_name"]

        db_host = Variable.get("db_host")
        db_name = Variable.get("db_name")
        db_user = Variable.get("db_user")
        db_password = Variable.get("db_password")
        db_port = '5432'

        if table_name == "weather_news":
            file_name = table_name + "list"

        else:
            file_name = table_name

        # s3에서 df형태로 데이터 가져오기
        df = s3_to_df(file_name)

        # 컬럼명 소문자로 변경 (psql 컬럼명은 소문자 기준)
        df.columns = df.columns.str.lower()
        
        # 혼잡도 레벨 one-hot encoding
        if table_name == 'congest':
            mapping = {'붐빔': 0, '약간 붐빔': 1, '보통': 2, '여유':3}
            df['congest_lvl_one_hot'] = df['area_congest_lvl'].map(mapping)

        # SQLAlchemy를 사용하여 RDS에 연결
        engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

        # DataFrame을 RDS 테이블로 적재
        df.to_sql(table_name, con=engine, if_exists='replace', index_label='id', dtype=data_type)
        with engine.connect() as con:
            if table_name == 'congest':
                create_query = """
                CREATE TABLE congest_temp AS(
                SELECT a.*, b.image
                FROM congest a INNER JOIN (SELECT category, image FROM seoul_data_image) b
                ON a.area_cd = b.category
                );
                """
                
                con.execute(create_query)
                con.execute("DROP TABLE congest;")
                con.execute("ALTER TABLE congest_temp RENAME TO congest;")

            con.execute(f"ALTER TABLE {table_name} ADD PRIMARY KEY (id);")
            



    except ValueError as e:
        print(kwargs)
        print(df[df.duplicated(subset="area_cd", keep=False)])

        raise AirflowException(f"df_to_rds ValueError 오류 발생. {e}")

    except Exception as e:
        raise AirflowException(f"df_to_rds 오류 발생. {e}")


dag = DAG(
    "s3_to_rds",
    default_args=default_args,
    schedule_interval='*/5 * * * *',
    catchup=False,
)


congest_s3_to_rds = PythonOperator(
    task_id="congest_s3_to_rds",
    python_callable=df_to_rds,
    params={
        'data_type':{
            "area_nm": String(100),
            "area_cd": String(20),
            "area_congest_lvl": String(20),
            "congest_lvl_one_hot": Integer(),
            "area_congest_msg": Text(),
            "area_ppltn_min": Integer(),
            "area_ppltn_max": Integer(),
            "male_ppltn_rate": Float(),
            "female_ppltn_rate": Float(),
            "ppltn_rate_0": Float(),
            "ppltn_rate_10": Float(),
            "ppltn_rate_20": Float(),
            "ppltn_rate_30": Float(),
            "ppltn_rate_40": Float(),
            "ppltn_rate_50": Float(),
            "ppltn_rate_60": Float(),
            "ppltn_rate_70": Float(),
            "resent_ppltn_rate": Float(),
            "non_resent_ppltn_rate": Float(),
            "timestamp": DateTime(),
            "area_category": String(100),
        },
        'table_name':'congest',
    },
    dag=dag,
)


congest_fcst_s3_to_rds = PythonOperator(
    task_id="congest_fcst_s3_to_rds",
    python_callable=df_to_rds,
    params={
        'data_type':{
            "area_nm": String(100),
            "area_cd": String(20),
            "timestamp": DateTime(),
            "fcst_time": DateTime(),
            "fcst_congest_lvl": String(20),
            "fcst_ppltn_min": Integer(),
            "fcst_ppltn_max": Integer(),    
        },
        'table_name':'congest_fcst',
    },
    dag=dag,
)

weather_s3_to_rds = PythonOperator(
    task_id="weather_s3_to_rds",
    python_callable=df_to_rds,
    params={
        'data_type':{
            "area_nm": String(100),
            "area_cd": String(20),
            "weather_time": DateTime(),
            "temp": Float(),
            "sensible_temp": String(20),
            "max_temp": String(20),
            "min_temp": String(20),
            "humidity": String(20),
            "wind_dirct": String(20),
            "wind_spd": String(20),
            "precipitation": String(100),
            "precpt_type": String(100),
            "pcp_msg": Text(),
            "sunrise":String(20),
            "sunset": String(20),
            "uv_index_lvl": Integer(),
            "uv_index": String(20),
            "uv_msg": Text(),
            "pm25_index": String(20),
            "pm25": String(20),
            "pm10_index": String(20),
            "pm10air_idx": String(20),
            "air_idx_mvl": String(20),
            "air_idx_main": String(20),
            "air_msg": Text(),
            "timestamp": DateTime(),
        },
        'table_name':'weather',
    },
    dag=dag,
)



weather_fcst_s3_to_rds = PythonOperator(
    task_id="weather_fcst_s3_to_rds",
    python_callable=df_to_rds,
    params={
        'data_type':{
            "area_nm":String(100),
            "area_cd": String(20),
            "timestamp": DateTime(),
            "fcst_dt": DateTime(),
            "temp": Integer(),
            "precipitation": String(30),
            "precpt_type": String(100),
            "rain_chance": Integer(),
            "sky_stts": String(30),
        },
        'table_name':'weather_fcst',
    },
    dag=dag,
)

weather_news_s3_to_rds = PythonOperator(
    task_id="weather_news_s3_to_rds",
    python_callable=df_to_rds,
    params={
        'data_type':{
            "area_nm":String(100),
            "area_cd": String(20),
            "timestamp": DateTime(),
            "fcst_dt": DateTime(),
            "temp": Integer(),
            "precipitation": String(30),
            "precpt_type": String(100),
            "rain_chance": Integer(),
            "sky_stts": String(30),
        },
        'table_name':'weather_news',
    },
    dag=dag,
)


congest_s3_to_rds  
congest_s3_to_rds 
weather_s3_to_rds 
weather_fcst_s3_to_rds
weather_news_s3_to_rds
