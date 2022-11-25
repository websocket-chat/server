#!/usr/bin/env bash
set -euo pipefail

execDBStatement() {
  if [[ "$DB_USE_SSL" == "true" ]]; then
    EXTRA_PARAMS="--ssl"
  else
    EXTRA_PARAMS=""
  fi

  mysql \
  --host=$DB_HOST \
  --port=$DB_PORT \
  --user=$DB_USER \
  --password=$DB_PASS \
  $EXTRA_PARAMS \
  --execute="$1"

  # postgres version
  # echo "$1" | PGPASSWORD=$DB_PASS psql \
  # --host=$DB_HOST \
  # --port=$DB_PORT \
  # --username=$DB_USER \
  # --dbname=postgres

}

FULL_DB_NAME="${DB_NAME}"

if [[ "$APP_COMPONENT" == "tests" ]]; then
  FULL_DB_NAME="${DB_NAME}_test"
fi

execDBStatement "CREATE DATABASE IF NOT EXISTS ${FULL_DB_NAME}"
