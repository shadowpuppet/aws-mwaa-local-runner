from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


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

    task2 = SQLExecuteQueryOperator(
        task_id="snowflake_check",
        conn_id="snowflake_conn_serviceaccount",
        sql="SHOW TABLES"
    )

task1 >> task2
