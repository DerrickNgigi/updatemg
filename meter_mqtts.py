import network
import utime
import ujson
import globals
import burner  # Importing the new hardware driver

# ==========================================
# CALLBACKS
# ==========================================

def conncb(task):
    print("[MQTT] Connected to %s:%d" % (globals.MQTT_BROKER, globals.MQTT_BROKER_PORT))

def disconncb(task):
    print("[MQTT] Disconnected")

def datacb(msg):
    """
    Handles incoming MQTT messages and delegates to burner.py
    Expected format: {"burner": 1, "command": "start"}
    """
    print("[MQTT] Received on %s: %s" % (msg[1], msg[2]))
    try:
        data = ujson.loads(msg[2])
        burner_idx = data.get("burner")
        command = data.get("command", "").lower()
        
        if command == "start":
            success = burner.control(burner_idx, 1)
            if success:
                print("Burner %d: ON" % burner_idx)
            else:
                print("Invalid burner index: %s" % burner_idx)
                
        elif command == "stop":
            success = burner.control(burner_idx, 0)
            if success:
                print("Burner %d: OFF" % burner_idx)
            else:
                print("Invalid burner index: %s" % burner_idx)
                
        else:
            print("Unknown command: %s" % command)
            
    except Exception as e:
        print("Error processing message: %s" % e)

# ==========================================
# INITIALIZATION
# ==========================================

def start_mqtt():
    """
    Initializes MQTT connection.
    No longer requires hardware arguments.
    """
    try:
        mqtt = network.mqtt(
            globals.MQTT_CLIENT_ID,
            globals.MQTT_BROKER,
            user=globals.MQTT_CLIENT_USERNAME,
            password=globals.MQTT_CLIENT_PASSWORD,
            clientid=globals.MQTT_CLIENT_ID,
            port=globals.MQTT_BROKER_PORT,
            autoreconnect=True,
            connected_cb=conncb,
            disconnected_cb=disconncb,
            data_cb=datacb
            )
        print("[MQTT] Initializing...")
    
        mqtt.start()
        utime.sleep(2)

        # Subscribe to topic
        mqtt.subscribe(globals.MQTT_TOPIC_SUBSCRIBE)
        print("Subscribed to topic: %s" % globals.MQTT_TOPIC_SUBSCRIBE)
        
        # Publish initial status
        status_msg = {"status": "connected", "type": "gsm_variant"}
        mqtt.publish(globals.MQTT_TOPIC_PUBLISH, ujson.dumps(status_msg))
        return mqtt
        
    except Exception as e:
        print("[MQTT] Initialization failed: %s." % e)
        return None
