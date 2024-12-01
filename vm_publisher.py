"""EE 250L Lab 04 Starter Code

Run vm_publisher.py in a separate terminal on your VM."""

# Team Members: Sonya Alexis and Ethan Palosh

# Repo Link: https://github.com/usc-ee250-fall2024/mqtt-sonya-and-ethan.git

import paho.mqtt.client as mqtt
import time
import threading

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    #subscribe to topics of interest here

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

import threading
import time

# parallel task/thread to read keyboard input
def kbd_thread():
        while True:
                # must hit enter to complete the input
                k = input("")
                if k == 'w':
                    print("w")
                    #send "w" character to rpi
                    client.publish("sonyaal/lcd", "w")
                elif k == 'a':
                    print("you pressed: a")
                    # send "a" character to rpi
                    # topic is “YOUR_USERNAME/led”
                    #send "LED_ON"
                    client.publish("sonyaal/led", "LED_ON")
                    client.publish("sonyaal/lcd", "a")
                elif k == 's':
                    print("s")
                    # send "s" character to rpi
                    client.publish("sonyaal/lcd", "s")
                elif k == 'd':
                    print("you pressed: d")
                    # send "d" character to rpi
                    # topic is “YOUR_USERNAME/led”
                    # send "LED_OFF"
                    client.publish("sonyaal/led", "LED_OFF")
                    client.publish("sonyaal/lcd", "d")

if __name__ == '__main__':
    # spawn a thread to read keyboard input, specifying the function to run
    thread = threading.Thread(target=kbd_thread)
    #thread.daemon = True
    # start the thread executing
    thread.start()

    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="broker.hivemq.com", port=1883, keepalive=60)
    client.loop_start()

    while True:
        # print("delete this line")
        time.sleep(1)
