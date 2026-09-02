#!/bin/bash
# Runs automatically on first `docker compose up` via postgres's
# docker-entrypoint-initdb.d mechanism. Creates one database per
# service, all inside the single PostgreSQL server container (see
# "Database Architecture" in README.md for why this is the right
# tradeoff at this project's scale).
set -e

for db in identity_db event_db booking_db payment_db notification_db refund_db analytics_db; do
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    SELECT 'CREATE DATABASE $db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db')\gexec
EOSQL
done
