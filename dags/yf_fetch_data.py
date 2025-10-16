from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum
from src.apps.fetch_data import run_fetch

with DAG(
    dag_id="yf_fetch_data",
    start_date=pendulum.datetime(2025, 10, 1, tz="Europe/Lisbon"),
    schedule="@daily",
    catchup=False,
) as dag:
    fetch = PythonOperator(
        task_id="fetch_all",
        python_callable=run_fetch,
        op_kwargs={"path": "/opt/airflow/stocks/"},
    )