#!/bin/sh

echo "Running startup script."

export ENVIRONMENT_STAGE="local"
echo "Airflow Environment is:" $ENVIRONMENT_STAGE

ssh -4 -i ${AIRFLOW_LOCAL_CONNECTIONS_DIR:-${PWD}}/files/keys/ssh_host.pem -fNT -o ServerAliveInterval=60 -o ServerAliveCountMax=10 -o ExitOnForwardFailure=yes -o StrictHostKeyChecking=no -L 5432:${RDS_HOST}:5432 ${SSH_ADDRESS}