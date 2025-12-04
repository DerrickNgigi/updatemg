from machine import Pin
from time import sleep
import network
import utime
import ujson
import gc

# MQTT Configuration
MQTT_BROKER = "152.42.139.67"
MQTT_BROKER_PORT = 18100
MQTT_CLIENT_USERNAME = "mega_10009" #"MEGA_KK_10001"
MQTT_CLIENT_PASSWORD = "mega_10009" #"MEGA_KK_10001"
MQTT_CLIENT_ID = "mega_10009" #"MEGA_KK_10001"
MQTT_TOPIC_SUBSCRIBE = "megagas/kayole/kitchenOne"
MQTT_TOPIC_PUBLISH = "megakitchen/kayole/kitchenStatus"

# Indication constants
SUCCESS = 2
ERROR = 4

# Pin setup for burners
pins = [18, 19, 21, 22] 
burners = [Pin(pin, Pin.OUT) for pin in pins]

# Onboard LED setup
indicator = Pin(13, Pin.OUT)

def set_channels(state, sleep_time):
    for i, burner in enumerate(burners):
        burner.value(state)
        print("Channel %d %s" % (i + 1, 'on' if state else 'off'))
        sleep(sleep_time)

def blink(times):
    for _ in range(times):
        indicator.value(1)
        utime.sleep(0.5)
        indicator.value(0)
        utime.sleep(0.5)

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    wifi_networks = {
        "MEGA GAS": "Mega@2025",
    }

    while not wlan.isconnected():
        for ssid, password in wifi_networks.items():
            print("Connecting to Wi-Fi: %s" % ssid)
            wlan.connect(ssid, password)
            for _ in range(600):  # Retry for 10 seconds
                if wlan.isconnected():
                    print("Connected to Wi-Fi: %s, IP: %s" % (ssid, wlan.ifconfig()[0]))
                    blink(SUCCESS)
                    return wlan
                utime.sleep(1)
            print("Failed to connect to %s" % ssid)

        print("Retrying Wi-Fi connection...")
        gc.collect()  # Trigger garbage collection
    return wlan

# MQTT Callbacks
def conncb(task):
    print("[MQTT] Connected to %s:%d" % (MQTT_BROKER, MQTT_BROKER_PORT))

def disconncb(task):
    print("[MQTT] Disconnected")
    print("Attempting reconnection...")
    initialize_mqtt()

def datacb(msg):
    print("[MQTT] Received on %s: %s" % (msg[1], msg[2]))
    try:
        data = ujson.loads(msg[2])
        burner = data.get("burner")
        command = data.get("command", "").lower()
        if 1 <= burner <= len(burners):
            if command == "start":
                burners[burner - 1].value(1)
                print("Burner %d: ON" % burner)
            elif command == "stop":
                burners[burner - 1].value(0)
                print("Burner %d: OFF" % burner)
        else:
            print("Invalid burner number: %d" % burner)
    except Exception as e:
        print("Error processing message: %s" % e)

def initialize_mqtt():
    while True:
        try:
            mqtt = network.mqtt(
                MQTT_CLIENT_ID,
                MQTT_BROKER,
                user=MQTT_CLIENT_USERNAME,
                password=MQTT_CLIENT_PASSWORD,
                port=MQTT_BROKER_PORT,
                autoreconnect=True,
                connected_cb=conncb,
                disconnected_cb=disconncb,
                data_cb=datacb
            )
            print("[MQTT] MQTT initialized and started")
        
            mqtt.start()
            utime.sleep(2)

            # Subscribe to topic
            mqtt.subscribe(MQTT_TOPIC_SUBSCRIBE)
            print("Subscribed to topic: %s" % MQTT_TOPIC_SUBSCRIBE)
            
            # Publish initial status
            status_msg = {"status": "connected"}
            mqtt.publish(MQTT_TOPIC_PUBLISH, ujson.dumps(status_msg))
            print("Published initial status to %s" % MQTT_TOPIC_PUBLISH)
            return mqtt
        except Exception as e:
            print("[MQTT] Initialization failed: %s. Retrying in 5 seconds..." % e)
            utime.sleep(5)
            gc.collect()  # Trigger garbage collection

# Main function
def main():  
    # Switch solenoids on and off as a test
    print("Switching on the solenoids")
    set_channels(1, 1)
    sleep(1)

    print("Switching off the solenoids")
    set_channels(0, 0.5)
    sleep(5)
    
    # Connect to WiFi, then MQTT
    wlan = connect_to_wifi()
    utime.sleep(2)
    mqtt = initialize_mqtt()    
    utime.sleep(3)
    
    while True:
        try:
            if not wlan.isconnected():
                print("[Wi-Fi] Disconnected. Reconnecting...")
                wlan = connect_to_wifi()
                mqtt = initialize_mqtt()
            utime.sleep(1)
        except Exception as e:
            print("Error in main loop: %s" % e)
            print("\nDisconnecting...")
            mqtt.stop()
            utime.sleep(5)
            gc.collect()  # Trigger garbage collection
            machine.reset()

if __name__ == "__main__":
    main()

