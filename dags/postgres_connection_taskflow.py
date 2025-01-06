import boto3
import logging
import psycopg2
from airflow.decorators import dag, task
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
def connect_via_ssh(schema_name):
    db_host = Variable.get("RDS_HOST")
    db_user = Variable.get("RDS_USER")  # This is the IAM user or role
    db_port = 5432
    region = "us-west-2"

    # print("Schema-name", schema_name)

    token = get_iam_token(db_host, db_port, db_user, region)
    # print("token---", token)
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

default_args = {"owner": "airflow"}

@dag(default_args=default_args, schedule=None, tags=['example_taskflow'])
def postgres_conn_dag_with_taskflow_api():
    """
    ### TaskFlow API Tutorial Documentation
    This is a simple ETL data pipeline example which demonstrates the use of
    the TaskFlow API using three simple tasks for Extract, Transform, and Load.
    Documentation that goes along with the Airflow TaskFlow API tutorial is
    located
    [here](https://airflow.apache.org/docs/stable/tutorial_taskflow_api.html)
    """

    @task()
    def debug_python_task():
        """
        #### Extract task
        A simple Extract task to get data ready for the rest of the data
        pipeline. In this case, getting data is simulated by reading from a
        hardcoded JSON string.
        """

        test_rds_usr = Variable.get("RDS_USER")
        print("TEST_RDS_USER", test_rds_usr)
        test_rds_schema = Variable.get("RDS_SCHEMA")
        print("TEST_RDS_SCHEMA", test_rds_schema)

        connect_via_ssh(test_rds_schema)
        # return connect_via_ssh()

    @task()
    def use_this_approach_in_real_dags():
        """
        #### Load task
        A simple Load task which takes in the result of the Transform task and
        instead of saving it to end user review, just prints it out.
        """

        real_dags_approach = SQLExecuteQueryOperator(
            task_id="use_this_approach_in_real_dags",
            sql="select * from {{ params.rds_schema }}.engagement_district_usage limit 5;",
            conn_id="test_postgres_iam_conn",
        )

    debug = debug_python_task()
    # real_dags_task = real_dags_approach()

postgres_conn_dag_with_taskflow_api = postgres_conn_dag_with_taskflow_api()
