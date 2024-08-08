import boto3
import psycopg2
import logging
from copy import deepcopy

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import (
    SQLExecuteQueryOperator
)
from airflow.models.connection import Connection

from airflow.providers.postgres.hooks.postgres import PostgresHook

def get_iam_token(host, port, user, region):
    client = boto3.client("rds")
    logging.info(user)
    token = client.generate_db_auth_token(DBHostname=host, Port=port, DBUsername=user, Region=region)
    return token


def connect_via_ssh():
    db_host = Variable.get("POSTGRES_DB_HOST")
    db_user = Variable.get("POSTGRES_DB_USER")  # This is the IAM user or role
    db_port = 5432
    region = 'us-west-2'
    
    token = get_iam_token(db_host, db_port, db_user, region)
    """Establish a connection to a postgres database."""
    conn = Connection.get_connection_from_secrets('test_postgres_iam_conn')
    conn_args = {
            "host": conn.host,
            "user": conn.login,
            "password": token,
            "dbname": conn.schema,
            "port": conn.port,
        }
    connection = psycopg2.connect(
            **conn_args
    )
    cursor = connection.cursor()
    cursor.execute("select * from information_schema.tables limit 5;")
    result = cursor.fetchall()
    print(result)
    cursor.close()
    connection.close()


with DAG(
    dag_id='POSTGRESS_CONNECTION_TESTING',
    schedule=None,
    params={'rds_schema': Variable.get('RDS_SCHEMA')}
) as dag:
    run_query = PythonOperator(
        task_id='run_query',
        python_callable=connect_via_ssh,
    )

    operator_query = SQLExecuteQueryOperator(
        task_id = 'operator_query',
        sql = "select * from {{ params.rds_schema }}.engagement_district_usage limit 5;",
        conn_id = 'test_postgres_iam_conn',
    )
