#!/bin/sh

echo 'Running sample prestartup script.'

export $(jq -r 'to_entries|map("\(.key)=\(.value)")|.[]' ${AIRFLOW_LOCAL_CONNECTIONS_DIR}/variables.json)

eval "$(aws configure export-credentials --format env)"

export RDS_PASSWORD="$(aws rds generate-db-auth-token --hostname ${RDS_HOST} --port 5432 --region us-west-2 --username ${RDS_USER})"

./mwaa-local-env build-image

./mwaa-local-env start
