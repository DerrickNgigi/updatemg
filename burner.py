from machine import Pin
from time import sleep
import globals

# Initialize Burner Pins based on globals
_burners = [Pin(pin, Pin.OUT) for pin in globals.BURNER_PINS]

def control(index, state):
    """
    Control a specific burner.
    index: 1-based index (e.g., 1 for the first burner)
    state: 1 for ON, 0 for OFF
    Returns: True if successful, False if invalid index
    """
    if isinstance(index, int) and 1 <= index <= len(_burners):
        _burners[index - 1].value(state)
        return True
    return False

def set_all(state):
    """Turn all burners on or off"""
    for b in _burners:
        b.value(state)

def test_sequence():
    """Runs a quick hardware test on boot"""
    print("[Hardware] Testing solenoids...")
    
    # All ON briefly
    set_all(1)
    sleep(5)
    
    # All OFF
    set_all(0)
    print("[Hardware] Test complete.")