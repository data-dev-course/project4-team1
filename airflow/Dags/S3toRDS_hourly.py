from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.exceptions import AirflowException
import pandas as pd
import boto3
import io
from sqlalchemy import create_engine, inspect, Integer, Float, DateTime, Text, String
from airflow.models import Variable

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
        current_date = datetime.now().strftime('%Y%m%d')
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
        print(kwargs)
        data_type = kwargs["params"]["data_type"]
        table_name = kwargs["params"]["table_name"]
        file_name = table_name

        db_host = Variable.get("db_host")
        db_name = Variable.get("db_name")
        db_user = Variable.get("db_user")
        db_password = Variable.get("db_password")
        db_port = '5432'

        # s3에서 df형태로 데이터 가져오기
        df = s3_to_df(file_name)
        # 컬럼명 소문자로 변경 (psql 컬럼명은 소문자 기준)
        df.columns = df.columns.str.lower()

        
        # SQLAlchemy를 사용하여 RDS에 연결
        engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

        # DataFrame을 RDS 테이블로 적재
        table_name = table_name+'_past'
        inspector = inspect(engine)
        df = df[['area_nm','area_cd','timestamp','area_congest_lvl','area_ppltn_min','area_ppltn_max']]

        if table_name in inspector.get_table_names():
            df.to_sql(table_name, con=engine, if_exists='append', index=False, dtype=data_type)
            with engine.connect() as con:
                del_query = f"""
                DELETE FROM {table_name}
                WHERE (area_cd, timestamp) IN (
                SELECT area_cd, timestamp
                FROM (
                    SELECT
                    area_cd,
                    timestamp,
                    ROW_NUMBER() OVER (PARTITION BY area_cd ORDER BY timestamp DESC) AS row_num
                    FROM {table_name}
                ) AS subquery
                WHERE row_num > 12
                );
                """
                con.execute(f"ALTER TABLE {table_name} ADD PRIMARY KEY (id);")
                con.execute(del_query)
        else:
            with engine.connect() as con:
                create_query =f"""
                    CREATE TABLE {table_name}(
                    id SERIAL PRIMARY KEY,
                    area_nm VARCHAR(100),
                    area_cd VARCHAR(20),
                    timestamp TIMESTAMP,
                    area_congest_lvl VARCHAR(20),
                    area_ppltn_min INT,
                    area_ppltn_max INT
                    )
                """
                con.execute(create_query)
            df.to_sql(table_name, con=engine, if_exists='append', index=False, dtype=data_type)


    except ValueError as e:
        print(kwargs)
        
        raise AirflowException(f"df_to_rds 오류 발생. {e}")

    except Exception as e:

        raise AirflowException(f"df_to_rds 오류 발생. {e}")


dag = DAG(
    "s3_to_rds_hourly",
    default_args=default_args,
    schedule_interval=timedelta(hours=1),
    catchup=False,
)


congest_past_s3_to_rds = PythonOperator(
    task_id="congest_past_s3_to_rds",
    python_callable=df_to_rds,
    params={
        'data_type':{
            "area_nm": String(100),
            "area_cd": String(20),
            "timestamp": DateTime(),
            "area_congest_lvl": String(20),
            "area_ppltn_min": Integer(),
            "area_ppltn_max": Integer(),
        },
        'table_name':'congest',
    },
    dag=dag,
)



congest_past_s3_to_rds
