#!/bin/bash
HOST="$1"
shift
CMD="$@"

echo "Waiting for PostgreSQL at $HOST..."
until pg_isready -h "$HOST" -U stockuser -d stockdb 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - executing command: $CMD"
exec $CMD
