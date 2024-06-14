import boto3
import sshtunnel
import psycopg2
from datetime import datetime

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator


def get_iam_token(host, port, user, region):
    client = boto3.client("rds")
    token = client.generate_db_auth_token(DBHostname=host, Port=port, DBUsername=user, Region=region)
    return token


def connect_via_ssh():
    ssh_host = Variable.get("SSH_HOST")
    ssh_port = 22
    ssh_user = Variable.get("SSH_USER")
    ssh_pkey = '/usr/local/airflow/files/private_key.pem'  # Path to your SSH private key file
    db_host = Variable.get("DB_HOST")
    db_user = Variable.get("DB_USER")  # This is the IAM user or role
    db_name = Variable.get("DB_NAME")
    db_port = 5432
    region = 'us-west-2'

    with sshtunnel.SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_pkey=ssh_pkey,
            remote_bind_address=(db_host, db_port)
    ) as tunnel:
        token = get_iam_token(db_host, db_port, db_user, region)
        connection = psycopg2.connect(
            user=db_user,
            password=token,
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            database=db_name,
            sslmode='require'
        )
        cursor = connection.cursor()
        cursor.execute("select * from information_schema.tables limit 5;")
        result = cursor.fetchall()
        print(result)
        cursor.close()
        connection.close()


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 6, 14),
}

dag = DAG(dag_id='postgress_connection_testing', default_args=default_args, schedule_interval='@hourly')

run_query = PythonOperator(
    task_id='run_query',
    python_callable=connect_via_ssh,
    dag=dag
)
