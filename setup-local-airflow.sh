#!/usr/bin/env bash

set -e

echo "Copying Airflow files to test runner"
cp -v ../dags/*.py ./dags/
cp -rv ../dags/callables ./dags/
cp -rv ../dags/callbacks ./dags/
cp -rv ../dags/dag_utils ./dags/
cp -rv ../dags/metadata ./dags/
cp -rv ../dags/queries ./dags/
