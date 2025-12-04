from machine import Pin
import utime
import gsm
import sys
import meter_mqtts
import burner  # Import the burner driver
import globals

# ==========================================
# HARDWARE SETUP (System Level)
# ==========================================

# Onboard LED setup (Burners are now handled in burner.py)
indicator = Pin(globals.INDICATOR_PIN, Pin.OUT)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def blink(times):
    for _ in range(times):
        indicator.value(1)
        utime.sleep(0.5)
        indicator.value(0)
        utime.sleep(0.5)

# ==========================================
# GSM CONNECTIVITY
# ==========================================

def connect_to_gsm():
    print("[GSM] Powering on Modem...")
    
    # 1. Power on the GSM module
    try:
        GSM_POWER = Pin(globals.MODEM_POWER_PIN, Pin.OUT)
        GSM_POWER.value(1)
    except Exception as e:
        print("[GSM] Power pin error:", e)

    # 2. Reset / Power Key Sequence
    try:
        MODEM_RST = Pin(globals.MODEM_RST_PIN, Pin.OUT)
        MODEM_RST.value(1)
        
        GSM_PWR = Pin(globals.MODEM_PWRKEY_PIN, Pin.OUT)
        GSM_PWR.value(1)
        utime.sleep_ms(200)
        GSM_PWR.value(0)
        utime.sleep_ms(1000)
        GSM_PWR.value(1)
    except Exception as e:
        print("[GSM] Power Key error:", e)

    # 3. Initialize GSM Module
    print("[GSM] Initializing stack...")
    
    try:
        gsm.start(tx=globals.MODEM_TX, rx=globals.MODEM_RX, apn=globals.GSM_APN, 
                  user=globals.GSM_USER, password=globals.GSM_PASS, roaming=True)
    except OSError:
        print("[GSM] Failed to start GSM stack.")
        return False

    # 4. Wait for AT command response
    print("[GSM] Waiting for AT response...")
    for retry in range(20):
        if gsm.atcmd('AT'):
            break
        else:
            sys.stdout.write('.')
            utime.sleep_ms(2000)
    else:
        print("\n[GSM] Modem not responding to AT commands!")
        return False

    # 5. Connect to Network
    print("\n[GSM] Connecting to network...")
    gsm.connect()

    # Wait for connection (Status 1 = Connected)
    timeout = 30
    while gsm.status()[0] != 1 and timeout > 0:
        utime.sleep(1)
        timeout -= 1
        sys.stdout.write('.')
    
    if gsm.status()[0] == 1:
        print('\n[GSM] Connected! IP:', gsm.ifconfig()[0])
        blink(globals.SUCCESS)
        return True
    else:
        print('\n[GSM] Connection failed. Status:', gsm.status())
        return False

# ==========================================
# MAIN LOOP
# ==========================================

def main():  
    print("--- MEGA GAS GSM CONTROLLER STARTING ---")
    
    # 1. Hardware Test
    burner.test_sequence()
    
    # 2. Connect to GSM
    gsm_connected = connect_to_gsm()
    
    if not gsm_connected:
        print("Fatal Error: Could not establish GSM connection.")

    # 3. Initialize MQTT (No arguments needed now)
    mqtt_client = meter_mqtts.start_mqtt()
    
    while True:
        try:
            # Check GSM Connection (Status 1 is Connected)
            current_status = gsm.status()[0]
            
            if current_status != 1:
                print("[GSM] Connection lost (Status %d). Reconnecting..." % current_status)
                if mqtt_client:
                    try: mqtt_client.stop()
                    except: pass
                
                # Retry GSM connection
                connect_to_gsm()
                # Re-init MQTT if GSM comes back
                if gsm.status()[0] == 1:
                    mqtt_client = meter_mqtts.start_mqtt()
            
            utime.sleep(2)
            
        except Exception as e:
            print("Error in main loop: %s" % e)
            print("Restarting system in 5 seconds...")
            utime.sleep(5)
            machine.reset()

if __name__ == "__main__":
    main()