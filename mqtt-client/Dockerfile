FROM python:3.9-slim

# Install system dependencies and MS ODBC Driver 17 for SQL Server
RUN apt-get update && apt-get install -y \
    gcc \
    unixodbc-dev \
    curl \
    apt-transport-https \
    gnupg && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install required Python packages
RUN pip install paho-mqtt pyodbc

WORKDIR /app
COPY mqtt_client.py /app/mqtt_client.py

CMD ["python", "mqtt_client.py"]
