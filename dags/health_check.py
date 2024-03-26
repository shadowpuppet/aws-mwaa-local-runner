from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator


def health_check():
    print("Health is good.")


with DAG(
        dag_id="health_check_dag",
        start_date=datetime(2024, 3, 26),
        schedule="@hourly",
        catchup=False,
) as dag:
    task1 = PythonOperator(
        task_id="health_check",
        python_callable=health_check,
    )
