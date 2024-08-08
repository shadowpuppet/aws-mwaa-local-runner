#!/bin/sh

echo 'Running sample startup script.'

chmod 400 ${AIRFLOW_LOCAL_CONNECTIONS_DIR:-${PWD}}/files/keys/rds_proxy_dev.pem;

ssh -4 -i ${AIRFLOW_LOCAL_CONNECTIONS_DIR:-${PWD}}/files/keys/rds_proxy_dev.pem -fNT -o ServerAliveInterval=60 -o ServerAliveCountMax=10 -o ExitOnForwardFailure=yes -o StrictHostKeyChecking=no -L 5432:${RDS_HOST}:5432 ${SSH_ADDRESS}