import boto3
import logging
import psycopg2

from airflow import DAG
from airflow.models import Variable
from airflow.models.connection import Connection
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


# This is meant for debugging purposes
# Use the approach from the operator_query task below
def get_iam_token(host, port, user, region):
    client = boto3.client("rds")
    logging.info(user)
    token = client.generate_db_auth_token(
        DBHostname=host, Port=port, DBUsername=user, Region=region
    )
    return token


# This is meant for debugging purposes
# Use the approach from the operator_query task below
def connect_via_ssh():
    db_host = Variable.get("RDS_HOST")
    db_user = Variable.get("RDS_USER")  # This is the IAM user or role
    db_port = 5432
    region = "us-west-2"

    token = get_iam_token(db_host, db_port, db_user, region)
    """Establish a connection to a postgres database."""
    conn = Connection.get_connection_from_secrets("test_postgres_iam_conn")
    conn_args = {
        "host": conn.host,
        "user": conn.login,
        "password": token,
        "dbname": conn.schema,
        "port": conn.port,
    }
    connection = psycopg2.connect(**conn_args)
    cursor = connection.cursor()
    cursor.execute("select * from information_schema.tables limit 5;")
    result = cursor.fetchall()
    print(result)
    cursor.close()
    connection.close()


with DAG(
    dag_id="POSTGRESS_CONNECTION_TESTING",
    schedule=None,
    params={"rds_schema": Variable.get("RDS_SCHEMA")},
) as dag:
    # This is meant for debugging purposes
    # Use the approach from the operator_query task below
    # If the run query task is successful, but operator query is not:
    # Ensure a password is set in your postgres connection
    # Check that the RDS password (environment variable) is not expired
    debug_python_task = PythonOperator(
        task_id="run_query",
        python_callable=connect_via_ssh,
    )

    # This is how you should connect in real dags
    use_this_approach_in_real_dags = SQLExecuteQueryOperator(
        task_id="operator_query",
        sql="select * from {{ params.rds_schema }}.engagement_district_usage limit 5;",
        conn_id="test_postgres_iam_conn",
    )
