from machine import Pin
from time import sleep

# Define the pin numbers
pin_numbers = [22, 21, 19, 18]

# Initialize the channels as Pin objects
channels = [Pin(pin, Pin.OUT) for pin in pin_numbers]

def set_channels(state):
    for i, channel in enumerate(channels):
        channel.value(state)
        print("Channel {} {}".format(i + 1, 'on' if state else 'off'))

def main():
    print("Switching off the solenoids")
    set_channels(0)

    print("Switching on the solenoids")
    sleep(3)

    for i, channel in enumerate(channels):
        channel.value(1)
        print("Channel {} on".format(i + 1))
        sleep(1)

if __name__ == "__main__":
    main()

