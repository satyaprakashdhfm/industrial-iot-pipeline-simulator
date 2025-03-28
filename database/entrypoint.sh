#!/bin/bash
# Start SQL Server in the background
/opt/mssql/bin/sqlservr &

echo "Waiting for SQL Server to start..."
max_tries=30
for i in $(seq 1 $max_tries); do
    /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -Q "SELECT 1" >/dev/null 2>&1 && break
    echo "Attempt $i/$max_tries: SQL Server not ready, waiting 15 seconds..."
    sleep 120
done

if [ $i -eq $max_tries ]; then
    echo "SQL Server did not start in time."
    exit 1
fi

echo "SQL Server is ready. Running init.sql..."
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -i /init.sql

# Bring the SQL Server process to the foreground to keep the container running.
wait
