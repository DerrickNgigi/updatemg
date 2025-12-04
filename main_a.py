from machine import Pin
import machine
import utime
import sys
import meter_mqtts
import burner
import globals
import ota_update
# Import the GSM functions directly from the meter_gsm file
from meter_gsm import gsmInitialization, gsmCheckStatus

# ==========================================
# HELPER FUNCTIONS
# ==========================================

# Onboard LED setup
indicator = Pin(globals.INDICATOR_PIN, Pin.OUT)

def blink(times):
    for _ in range(times):
        indicator.value(1)
        utime.sleep(0.5)
        indicator.value(0)
        utime.sleep(0.5)

def sys_log(msg, log_type="INFO"):
    print("[{}] {}".format(log_type, msg))

# ==========================================
# MAIN LOOP
# ==========================================

def main():  
    print("--- MEGA GAS GSM CONTROLLER STARTING ---")
    
    # 1. Hardware Test
    burner.test_sequence()
    
    # 2. GSM Connection
    # We use the imported function to start the modem
    gsmInitialization()
    
    # Loop until connected or timeout (User defined logic)
    wait = 0
    while gsmCheckStatus() != 1:
        print("Waiting for GSM...")
        wait += 1
        utime.sleep(1)
        if wait > 120: 
             sys_log("GSM Timeout. Rebooting.", "ERROR")
             machine.reset()
            
    # Connected
    blink(globals.SUCCESS)
    sys_log("GSM Connected successfully.")

    # 3. Perform OTA Check
    try:
        sys_log("Checking for OTA Updates...")
        # Check for device-specific globals update first
        ota_update.update_global_file(globals.MQTT_CLIENT_ID, retries=3)
        # Then proceed with main firmware OTA
        ota_update.run_ota()
    except Exception as e:
        sys_log("OTA Check failed: {}".format(e), "WARN")

    # 4. Initialize MQTT
    # Since we are already connected, we can start MQTT
    mqtt_client = meter_mqtts.start_mqtt()
    
    while True:
        try:
            # Check GSM Connection (1 = Connected)
            if gsmCheckStatus() != 1:
                sys_log("GSM Connection lost. Reconnecting...", "WARN")
                
                # Stop MQTT to prevent errors
                if mqtt_client:
                    try: mqtt_client.stop()
                    except: pass
                
                # Retry Connection logic
                gsmInitialization()
                
                # Fast wait loop for reconnection
                wait = 0
                while gsmCheckStatus() != 1 and wait < 60:
                    utime.sleep(1)
                    wait += 1
                    
                if gsmCheckStatus() == 1:
                    mqtt_client = meter_mqtts.start_mqtt()
                else:
                     sys_log("Reconnection failed. Retrying in loop...", "ERROR")
            
            utime.sleep(2)
            
        except Exception as e:
            sys_log("Error in main loop: {}".format(e), "ERROR")
            sys_log("Restarting system in 5 seconds...", "WARN")
            utime.sleep(5)
            machine.reset()

if __name__ == "__main__":
    main()