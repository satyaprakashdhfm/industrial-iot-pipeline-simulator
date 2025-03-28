import time
import json
import logging
import datetime
import socket
import threading
from opcua import Server
import paho.mqtt.client as mqtt

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("gateway")
logging.getLogger("opcua").setLevel(logging.CRITICAL)
logging.getLogger("paho").setLevel(logging.CRITICAL)

# OPC UA Server settings
SERVER_ENDPOINT = "opc.tcp://0.0.0.0:4840"
SERVER_NAME = "OPC UA Gateway Server"
NAMESPACE = "SENSOR_DATA"

# MQTT settings
MQTT_BROKER = "mqtt-broker"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "opcua_gateway"
TOPIC_MACHINE1 = "machine1/sensor"
TOPIC_MACHINE2 = "machine2/sensor"

# Global flag for MQTT connection
mqtt_connected = False

def on_connect(client, userdata, flags, rc, properties=None):
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        logger.info("Connected to MQTT broker")
    else:
        logger.warning(f"MQTT connection failed with code {rc}")

def on_disconnect(client, userdata, rc, properties=None):
    global mqtt_connected
    mqtt_connected = False
    logger.info("Disconnected from MQTT broker")

def create_mqtt_client():
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True, protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    return client

def mqtt_connection_manager(client):
    try:
        resolved = socket.gethostbyname(MQTT_BROKER)
        logger.info(f"Resolved MQTT broker '{MQTT_BROKER}' to {resolved}")
    except Exception as e:
        logger.error(f"Failed to resolve MQTT broker '{MQTT_BROKER}': {e}")
        resolved = MQTT_BROKER
    client.loop_start()
    while True:
        if not mqtt_connected:
            try:
                client.connect(resolved, MQTT_PORT, keepalive=60)
                time.sleep(5)
            except Exception as e:
                logger.error(f"MQTT connection error: {e}")
        time.sleep(10)

def main():
    # Initialize OPC UA server
    server = Server()
    server.set_endpoint(SERVER_ENDPOINT)
    server.set_server_name(SERVER_NAME)
    nsidx = server.register_namespace(NAMESPACE)
    logger.info(f"Registered namespace '{NAMESPACE}' with index {nsidx}")

    # Create folder structure for sensors
    objects = server.get_objects_node()
    sensors_folder = objects.add_folder(nsidx, "Sensors")

    # Machine1 nodes
    m1_folder = sensors_folder.add_folder(nsidx, "Machine1")
    m1_temp = m1_folder.add_variable(f"ns={nsidx};s=Machine1_Temperature", "Temperature", 0.0)
    m1_press = m1_folder.add_variable(f"ns={nsidx};s=Machine1_Pressure", "Pressure", 0.0)
    m1_ts = m1_folder.add_variable(f"ns={nsidx};s=Machine1_Timestamp", "Timestamp", "")
    m1_temp.set_writable()
    m1_press.set_writable()
    m1_ts.set_writable()

    # Machine2 nodes
    m2_folder = sensors_folder.add_folder(nsidx, "Machine2")
    m2_temp = m2_folder.add_variable(f"ns={nsidx};s=Machine2_Temperature", "Temperature", 0.0)
    m2_press = m2_folder.add_variable(f"ns={nsidx};s=Machine2_Pressure", "Pressure", 0.0)
    m2_ts = m2_folder.add_variable(f"ns={nsidx};s=Machine2_Timestamp", "Timestamp", "")
    m2_temp.set_writable()
    m2_press.set_writable()
    m2_ts.set_writable()

    server.start()
    logger.info(f"OPC UA Server started at {SERVER_ENDPOINT}")

    # Start MQTT client
    mqtt_client = create_mqtt_client()
    mqtt_thread = threading.Thread(target=mqtt_connection_manager, args=(mqtt_client,), daemon=True)
    mqtt_thread.start()

    # Initialize last payloads as None for change detection
    last_m1_payload = None
    last_m2_payload = None

    try:
        while True:
            # Read Machine1 sensor values
            m1_temp_val = m1_temp.get_value()
            m1_press_val = m1_press.get_value()
            m1_ts_val = m1_ts.get_value()

            # Read Machine2 sensor values
            m2_temp_val = m2_temp.get_value()
            m2_press_val = m2_press.get_value()
            m2_ts_val = m2_ts.get_value()

            payload_m1 = json.dumps({
                "timestamp": m1_ts_val,
                "temperature": m1_temp_val,
                "pressure": m1_press_val
            })
            payload_m2 = json.dumps({
                "timestamp": m2_ts_val,
                "temperature": m2_temp_val,
                "pressure": m2_press_val
            })

            if mqtt_connected:
                # Publish only if payload has changed for Machine1
                if payload_m1 != last_m1_payload:
                    result1 = mqtt_client.publish(TOPIC_MACHINE1, payload_m1)
                    if result1.rc == mqtt.MQTT_ERR_SUCCESS:
                        logger.info(f"Published to {TOPIC_MACHINE1}: {payload_m1}")
                        last_m1_payload = payload_m1
                    else:
                        logger.warning(f"Failed to publish to {TOPIC_MACHINE1}, code: {result1.rc}")

                # Publish only if payload has changed for Machine2
                if payload_m2 != last_m2_payload:
                    result2 = mqtt_client.publish(TOPIC_MACHINE2, payload_m2)
                    if result2.rc == mqtt.MQTT_ERR_SUCCESS:
                        logger.info(f"Published to {TOPIC_MACHINE2}: {payload_m2}")
                        last_m2_payload = payload_m2
                    else:
                        logger.warning(f"Failed to publish to {TOPIC_MACHINE2}, code: {result2.rc}")
            else:
                logger.info("MQTT not connected, skipping publish")

            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Shutting down gateway...")
    finally:
        mqtt_client.loop_stop()
        server.stop()
        logger.info("OPC UA Server stopped")

if __name__ == "__main__":
    main()
