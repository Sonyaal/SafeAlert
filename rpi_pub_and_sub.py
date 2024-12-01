"""EE 250L Lab 04 Starter Code

Run rpi_pub_and_sub.py on your Raspberry Pi."""

# Team Members: Sonya Alexis and Ethan Palosh

# Repo Link: https://github.com/usc-ee250-fall2024/mqtt-sonya-and-ethan.git

import paho.mqtt.client as mqtt
import time
import sys
import grovepi
from grove_rgb_lcd import *

# By appending the folder of all the GrovePi libraries to the system path here,
# we are successfully `import grovepi`
sys.path.append('../../Software/Python/')
# This append is to support importing the LCD library.
sys.path.append('../../Software/Python/grove_rgb_lcd')

# Defining GrovePi ports
led_port = 4  # D4
ultrasonic_ranger_port = 3  # D3
button_port = 2 #D2

# Initialize the LED as an output
grovepi.pinMode(led_port, "OUTPUT")

# Custom callback for LED control
def on_led_message(client, userdata, msg):
    message = msg.payload.decode("utf-8")
    if message == "LED_ON":
        print("Turning LED on")
        # Turning LED on 
        grovepi.digitalWrite(led_port, 1)
    elif message == "LED_OFF":
        print("Turning LED off")
        # Turning LED off
        grovepi.digitalWrite(led_port, 0) 
    else:
        # Error handling if we don't get an expected message
        print("Received unknown message:", message)

# Callback for LCD message
def on_lcd_message(client, userdata, msg):
    message = msg.payload.decode("utf-8")

    if message == "w":
        setText("Last Message - W")
    elif message == "a":
        setText("Last Message - A")
    elif message == "s":
        setText("Last Message - S")
    elif message == "d":
        setText("Last Message - D")
    else:
        # Error handling if we don't get an expected message
        print("Received unknown message:", message)

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to topics of interest here
    client.subscribe("sonyaal/led")
    client.subscribe("sonyaal/lcd")

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect

    # Set custom callback for the LED topic
    client.message_callback_add("sonyaal/led", on_led_message)

    client.message_callback_add("sonyaal/lcd", on_lcd_message)

    client.connect(host="broker.hivemq.com", port=1883, keepalive=60)
    client.loop_start()

    setRGB(230, 230, 250)
    setText("Awaiting a message...")

    while True:
        # print("delete this line")
        # time.sleep(1)
        try:
            # Read the ultrasonic ranger value
            distance = grovepi.ultrasonicRead(ultrasonic_ranger_port)
            
            # Publish the distance to the ultrasonicRanger topic
            client.publish("sonyaal/ultrasonicRanger", str(distance))
            print("Published distance:", distance, "cm")
            
            # Button value
            button_value = grovepi.digitalRead(button_port)

            print("BUTTON: " + str(button_value))

            if(button_value == 1):
                client.publish("sonyaal/button", "Button pressed!")
            else:
                client.publish("sonyaal/button", "Button NOT pressed.")



            # Sleep for 1 second
            time.sleep(1)
        
        except IOError:
            print("Error reading from GrovePi device")
