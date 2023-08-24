from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd
import psycopg2
import boto3
import io
from airflow.models import Variable

default_args = {
    "owner": "pjm",
    "depends_on_past": False,
    "start_date": datetime(2023, 8, 23),
    "retries": 1,
    "retry_delay": timedelta(seconds=1),
}


def move_s3_to_rds(s3_key, table_name, column_mapping):
    s3_bucket = Variable.get("s3_bucket_name")

    db_host = Variable.get("db_host")
    db_name = Variable.get("db_name")
    db_user = Variable.get("db_user")
    db_password = Variable.get("db_password")

    # Connect to S3
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    data = response["Body"].read().decode("utf-8")

    # Parse CSV data using pandas
    df = pd.read_csv(io.StringIO(data))

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=db_host, dbname=db_name, user=db_user, password=db_password
    )
    cursor = conn.cursor()

    # Check if the table exists
    check_table_query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}')"
    cursor.execute(check_table_query)
    table_exists = cursor.fetchone()[0]

    if table_exists:
        # Delete existing data in the table
        delete_query = f"DELETE FROM {table_name}"
        cursor.execute(delete_query)
        conn.commit()

    # Create table if not exists
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join(f"{col} {col_type}" for col, col_type in column_mapping.items())}
        )
    """
    cursor.execute(create_table_query)
    conn.commit()

    # Insert data into PostgreSQL
    insert_query = f"INSERT INTO {table_name} ({', '.join(column_mapping.keys())}) VALUES ({', '.join(['%s'] * len(column_mapping))})"
    for index, row in df.iterrows():
        cursor.execute(insert_query, tuple(row[col] for col in column_mapping.keys()))

    conn.commit()
    conn.close()


dag = DAG(
    "s3_to_rds_dag_test_1",
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    catchup=False,
)

move_congest_data_task = PythonOperator(
    task_id="move_congest_data_task",
    python_callable=move_s3_to_rds,
    op_args=[
        "area_data/강남 MICE 관광특구/20230823/area_data-강남 MICE 관광특구-congest_data_20230823.csv",
        "congestion_t",
        {
            "AREA_NM": "VARCHAR(255)",
            "AREA_CD": "VARCHAR(255)",
            "AREA_CONGEST_LVL": "VARCHAR(255)",
            "AREA_CONGEST_MSG": "VARCHAR(255)",
            "AREA_PPLTN_MIN": "INTEGER",
            "AREA_PPLTN_MAX": "INTEGER",
            "MALE_PPLTN_RATE": "FLOAT",
            "FEMALE_PPLTN_RATE": "FLOAT",
            "PPLTN_RATE_0": "FLOAT",
            "PPLTN_RATE_10": "FLOAT",
            "PPLTN_RATE_20": "FLOAT",
            "PPLTN_RATE_30": "FLOAT",
            "PPLTN_RATE_40": "FLOAT",
            "PPLTN_RATE_50": "FLOAT",
            "PPLTN_RATE_60": "FLOAT",
            "PPLTN_RATE_70": "FLOAT",
            "RESNT_PPLTN_RATE": "FLOAT",
            "NON_RESNT_PPLTN_RATE": "FLOAT",
            "TIMESTAMP": "TIMESTAMP",
            "AREA_CATEGORY": "VARCHAR(255)",
        },
    ],
    dag=dag,
)

move_congest_fcst_data_task = PythonOperator(
    task_id="move_congest_fcst_data_task",
    python_callable=move_s3_to_rds,
    op_args=[
        "area_data/강남 MICE 관광특구/20230823/area_data-강남 MICE 관광특구-congest_fcst_data_20230823.csv",
        "congestion_forecast_t",
        {
            "AREA_NM": "VARCHAR(255)",
            "AREA_CD": "VARCHAR(255)",
            "TIMESTAMP": "TIMESTAMP",
            "FCST_TIME": "TIMESTAMP",
            "FCST_CONGEST_LVL": "VARCHAR(255)",
            "FCST_PPLTN_MIN": "INT",
        },
    ],
    dag=dag,
)

move_weather_fcst_data_task = PythonOperator(
    task_id="move_weather_fcst_data_task",
    python_callable=move_s3_to_rds,
    op_args=[
        "area_data/강남 MICE 관광특구/20230823/area_data-강남 MICE 관광특구-weather_fcst_data_20230823.csv",
        "weather_forecast_t",
        {
            "AREA_NM": "VARCHAR(255)",
            "AREA_CD": "VARCHAR(255)",
            "TIMESTAMP": "TIMESTAMP",
            "FCST_DT": "TIMESTAMP",
            "TEMP": "INT",
            "PRECIPITATION": "VARCHAR(255)",
            "PRECPT_TYPE": "VARCHAR(255)",
            "RAIN_CHANCE": "INT",
            "SKY_STTS": "VARCHAR(255)",
        },
    ],
    dag=dag,
)

move_weather_data_task = PythonOperator(
    task_id="move_weather_data_task",
    python_callable=move_s3_to_rds,
    op_args=[
        "area_data/강남 MICE 관광특구/20230823/area_data-강남 MICE 관광특구-weather_data_20230823.csv",
        "weather_t",
        {
            "AREA_NM": "VARCHAR(255)",
            "AREA_CD": "VARCHAR(255)",
            "WEATHER_TIME": "TIMESTAMP",
            "TEMP": "FLOAT",
            "SENSIBLE_TEMP": "FLOAT",
            "MAX_TEMP": "FLOAT",
            "MIN_TEMP": "FLOAT",
            "HUMIDITY": "INT",
            "WIND_DIRCT": "VARCHAR(255)",
            "WIND_SPD": "FLOAT",
            "PRECIPITATION": "VARCHAR(255)",
            "PRECPT_TYPE": "VARCHAR(255)",
            "PCP_MSG": "VARCHAR(255)",
            "SUNRISE": "VARCHAR(255)",
            "SUNSET": "VARCHAR(255)",
            "UV_INDEX_LVL": "INT",
            "UV_INDEX": "VARCHAR(255)",
            "UV_MSG": "VARCHAR(255)",
            "PM25_INDEX": "VARCHAR(255)",
            "PM25": "INT",
            "PM10_INDEX": "VARCHAR(255)",
            "PM10AIR_IDX": "VARCHAR(255)",
            "AIR_IDX_MVL": "INT",
            "AIR_IDX_MAIN": "VARCHAR(255)",
            "AIR_MSG": "VARCHAR(255)",
            "TIMESTAMP": "TIMESTAMP",
        },
    ],
    dag=dag,
)

move_congest_data_task >> move_congest_fcst_data_task >> move_weather_data_task >> move_weather_fcst_data_task
