import datetime
from datetime import datetime, timedelta
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from airflow import DAG
import seoul_api_data


default_args = {
    "owner": "swanim",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=1),
    "start_date": datetime(2023, 8, 25, 6, 50),
    "catchup": False,
    "tags": ["seoul_api"],
}

dag = DAG(
    "seoul_api_dag",
    default_args=default_args,
    schedule_interval="*/5 * * * *",
)


area_list = eval(Variable.get("area_list_dag1"))
base_url = Variable.get("seoul_openapi_url")
area_category = eval(Variable.get("area_category_1"))

area_list2 = eval(Variable.get("area_list_dag2"))
base_url2 = Variable.get("seoul_openapi_url2")
area_category2 = eval(Variable.get("area_category_2"))

run_task = PythonOperator(
    task_id="area_list1",
    python_callable=seoul_api_data.run_sync,
    op_args=[area_list, base_url, area_category],
    dag=dag,
)

run_task2 = PythonOperator(
    task_id="area_list2",
    python_callable=seoul_api_data.run_sync,
    op_args=[area_list2, base_url2, area_category2],
    dag=dag,
)

run_task
run_task2
