# ==========================================
# MQTT CONFIGURATION
# ==========================================
MQTT_BROKER = "152.42.139.67"
MQTT_BROKER_PORT = 18100
MQTT_CLIENT_USERNAME = "mega_10006"
MQTT_CLIENT_PASSWORD = "mega_10006"
MQTT_CLIENT_ID = "mega_10006"

MQTT_TOPIC_SUBSCRIBE = "megagas/mega_10006/kitchen"
MQTT_TOPIC_PUBLISH = "megagas/mega_10006/kitchenStatus"

# ==========================================
# GSM CONFIGURATION (APN)
# ==========================================
GSM_APN = "safaricomiot"
GSM_USER = ""
GSM_PASS = ""

# ==========================================
# OTA CONFIGURATION
# ==========================================
UPDATE_URL = "https://raw.githubusercontent.com/DerrickNgigi/updatemg/main"
VERSION_FILE = "/flash/version.txt"
GLOBAL_VERSION = "1.0.3"

# ==========================================
# HARDWARE PIN CONFIGURATION
# ==========================================

# Modem Pins (SIM800L / TTGO T-Call)
MODEM_POWER_PIN = 23
MODEM_PWRKEY_PIN = 4
MODEM_RST_PIN = 5
MODEM_TX = 27
MODEM_RX = 26

# Application Pins
INDICATOR_PIN = 13
BURNER_PINS = [18, 19, 21, 22]  # [Burner 1, Burner 2, Burner 3, Burner 4]

# Indication constants
SUCCESS = 2
ERROR = 4