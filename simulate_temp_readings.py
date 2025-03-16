import random
import time
import logging
import argparse
from logging.handlers import RotatingFileHandler
import os
from azure.iot.device import IoTHubDeviceClient, Message
from azure.iot.device.exceptions import IoTHubError

# The connection string you got from Azure IoT Hub (the primary connection string from your screenshot)
CONNECTION_STRING = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")

def handle_launch_params():
    time_interval = 60
    parser = argparse.ArgumentParser()
    parser.add_argument("--time_interval", type=int, help="telemetry hz")
    args = parser.parse_args()

    if (args.time_interval):
        time_interval = args.time_interval

    return time_interval

def setup_logging(name, filename):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_format = format='%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)

    # Set up file handler
    log_file = os.path.join(log_dir, filename)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024*1024,
        backupCount=1,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    #setup console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # config root logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger 

def simulate_temperature():
    """Simulate temperature readings"""
    return round(random.uniform(20.0, 40.0), 2)

def main():
    try:
        if not CONNECTION_STRING:
            raise ValueError("Enviroment variabel IOTHUB_DEVICE_CONNECTION_STRING is not set")

        time_interval = handle_launch_params()
        app_logger = setup_logging("application", "application.log")
        temp_logger = setup_logging("telemetry", "telemetry.log")
        alert_logger = setup_logging("alerts", "alert.log")
        error_logger = setup_logging("error", "error.log")
        
        # Create an IoT Hub client
        client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
        app_logger.info("Device connected to IoT Hub")

        while True:
            # Simulate temperature reading
            temperature = simulate_temperature()
            if (temperature > 35) :
                alert_logger.log("")

            # Create message object
            message = Message(str({
                'temperature': temperature,
                'timestamp': time.time()
            }))

            try: # Send the message
                client.send_message(message)
                temp_logger.info(f"Temperature {temperature}")
            except Exception as e:
                error_logger.error(f"Unexpected error sending message: {str(e)}")

            
            time.sleep(time_interval)

    except ValueError as e:
        app_logger.error(f"Value error: {e}")
        client.shutdown()
    except KeyboardInterrupt:
        app_logger.log("App stopped by the user")
        client.shutdown()
    finally:
        app_logger.log("App stopped")
        client.shutdown()

if __name__ == "__main__":
    main()