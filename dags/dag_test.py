import json
from airflow.models import Variable
from airflow.configuration import conf

airflow_home = "/home/seesaw/airflow"
var_file_path = airflow_home + json.loads(conf.get("secrets", "backend_kwargs"))["variables_file_path"]
conn_file_path = airflow_home + json.loads(conf.get("secrets", "backend_kwargs"))["connections_file_path"]

print(var_file_path)
print(conn_file_path)


if __name__ == "__main__":

    # without any airflow variable.
    from example_dag_with_taskflow_api import dag_with_taskflow_api as dag_test
    dag_test.test(
        variable_file_path=var_file_path
    )


    # with airflow env-variable
    # from postgres_connection_example import dag as postgres_dag_test
    # postgres_dag_test.test(
    #     variable_file_path=variables_path,
    #     conn_file_path=connections_path,
    # )

    from postgres_connection_taskflow import postgres_conn_dag_with_taskflow_api as postgres_dag_test_taskflow
    postgres_dag_test_taskflow.test(
        variable_file_path=var_file_path,
        conn_file_path=conn_file_path,
    )
