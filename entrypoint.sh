#!/bin/sh
set -e
envsubst < /app/profiles.yml > /root/.dbt/profiles.yml
exec "$@"
