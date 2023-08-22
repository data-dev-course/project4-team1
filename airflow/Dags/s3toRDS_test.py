from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
import psycopg2
import boto3
import io
from airflow.models import Variable

default_args = {
    "owner": "your_name",
    "depends_on_past": False,
    "start_date": datetime(2023, 8, 21),
    "retries": 1,
    "retry_delay": timedelta(seconds=1),
}


def move_s3_to_rds():
    s3_bucket = Variable.get("s3_bucket_name")
    s3_key = "s3_to_rds_test/congest_data_test.csv"

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

    # Insert data into PostgreSQL
    insert_query = (
        "INSERT INTO test1 (AREA_NM, AREA_CD, AREA_CONGEST_LVL) VALUES (%s, %s, %s)"
    )
    for index, row in df.iterrows():
        cursor.execute(
            insert_query, (row["AREA_NM"], row["AREA_CD"], row["AREA_CONGEST_LVL"])
        )

    conn.commit()
    conn.close()


dag = DAG(
    "s3_to_rds_dag_variable_test",
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    catchup=False,
)

move_data_task = PythonOperator(
    task_id="move_data_task",
    python_callable=move_s3_to_rds,
    dag=dag,
)
