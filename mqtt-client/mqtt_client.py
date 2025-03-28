import os
import json
import logging
import time
import paho.mqtt.client as mqtt
import pyodbc
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mqtt_client")

# MQTT settings
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt-broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPICS = [("machine1/sensor", 0), ("machine2/sensor", 0)]

# Database connection parameters
DB_SERVER = os.getenv("DB_SERVER", "mssql")
DB_DATABASE = os.getenv("DB_DATABASE", "SensorDB")
DB_USERNAME = os.getenv("DB_USERNAME", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "YourStrong!Passw0rd")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

def get_db_connection():
    conn_str = (
        f"DRIVER={DB_DRIVER};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};"
        f"PWD={DB_PASSWORD};"
        "Timeout=10;"
    )
    retries = 15
    while retries:
        try:
            return pyodbc.connect(conn_str)
        except Exception as e:
            logger.error(f"DB connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(10)
            retries -= 1
    raise Exception("Could not connect to DB after several retries")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker")
        client.subscribe(TOPICS)
    else:
        logger.error(f"Failed to connect to MQTT broker with code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        # Determine Machine ID from topic name
        machine_id = "Machine1" if msg.topic == "machine1/sensor" else "Machine2"
        timestamp_str = data.get("timestamp")  # Example: '2025-03-28T05:46:57.513491'
        temperature = data.get("temperature")
        pressure = data.get("pressure")

        logger.info(f"Received data from {machine_id}: {data}")

        # Convert timestamp to SQL Server datetime format
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            logger.error(f"Timestamp conversion error: {e}")
            return

        # Insert data into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO SensorData (MachineID, Timestamp, Temperature, Pressure)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(sql, machine_id, timestamp, temperature, pressure)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Data inserted into database")

    except Exception as e:
        logger.error(f"Error processing message: {e}")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "mqtt_client")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()
