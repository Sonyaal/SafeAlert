"""EE 250L Lab 04 Starter Code

Run vm_subscriber.py in a separate terminal on your VM."""

# Team Members: Sonya Alexis and Ethan Palosh

# Repo Link: https://github.com/usc-ee250-fall2024/mqtt-sonya-and-ethan.git

import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to the ultrasonic ranger topic here
    client.subscribe("sonyaal/ultrasonicRanger")

    # subscribing to button topic
    client.subscribe("sonyaal/button")


# Custom callback that prints the ultrasonic ranger values
def on_ultrasonic_message(client, userdata, msg):
    # Convert payload to string using python string decode method
    message = msg.payload.decode("utf-8")
    # Prints the ultrasonic ranger values received from the RPi
    print("VM:", message, "cm")

def on_button_message(client, userdata, msg):
    # Convert payload to string using python string decode method
    message = msg.payload.decode("utf-8")
    # Prints the ultrasonic ranger values received from the RPi
    print(message)

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect

    # Set custom callback for the ultrasonic ranger topic
    client.subscribe("sonyaal/ultrasonicRanger")
    client.message_callback_add("sonyaal/ultrasonicRanger", on_ultrasonic_message)

    client.subscribe("sonyaal/button")
    client.message_callback_add("sonyaal/button", on_button_message)

    client.connect(host="broker.hivemq.com", port=1883, keepalive=60)
    client.loop_start()

    while True:
        # print("delete this line")
        time.sleep(1)
            

