import time
import random
import logging
import datetime
import os
from opcua import Client
from opcua import ua

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("machine2")
logging.getLogger("opcua").setLevel(logging.CRITICAL)

# Read configuration from environment variables
OPCUA_SERVER_URL = os.getenv("OPCUA_SERVER_URL", "opc.tcp://gateway:4840")
MACHINE_ID = os.getenv("MACHINE_ID", "Machine2")
SAMPLE_INTERVAL = int(os.getenv("SAMPLE_INTERVAL", "15"))
NAMESPACE = os.getenv("NAMESPACE", "SENSOR_DATA")

TEMP_MIN = 20.0
TEMP_MAX = 35.0
PRESS_MIN = 995.0
PRESS_MAX = 1025.0

def main():
    client = Client(OPCUA_SERVER_URL)
    connected = False
    while not connected:
        try:
            logger.info(f"Connecting to OPC UA server at {OPCUA_SERVER_URL}")
            client.connect()
            connected = True
            logger.info("Connected to OPC UA server")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            time.sleep(10)

    try:
        nsidx = client.get_namespace_index(NAMESPACE)
        logger.info(f"Using namespace '{NAMESPACE}' with index {nsidx}")

        temp_node = client.get_node(f"ns={nsidx};s={MACHINE_ID}_Temperature")
        press_node = client.get_node(f"ns={nsidx};s={MACHINE_ID}_Pressure")
        ts_node = client.get_node(f"ns={nsidx};s={MACHINE_ID}_Timestamp")

        while True:
            temp = round(random.uniform(TEMP_MIN, TEMP_MAX), 2)
            press = round(random.uniform(PRESS_MIN, PRESS_MAX), 2)
            current_time = datetime.datetime.utcnow().isoformat()

            temp_node.set_value(ua.DataValue(ua.Variant(temp, ua.VariantType.Float)))
            press_node.set_value(ua.DataValue(ua.Variant(press, ua.VariantType.Float)))
            ts_node.set_value(ua.DataValue(ua.Variant(current_time, ua.VariantType.String)))

            logger.info(f"Machine2 - Temperature: {temp}°C, Pressure: {press} hPa, Timestamp: {current_time}")
            time.sleep(SAMPLE_INTERVAL)
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client.disconnect()
        logger.info("Disconnected from OPC UA server")

if __name__ == "__main__":
    main()
