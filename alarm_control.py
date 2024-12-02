import paho.mqtt.client as mqtt
import time

alert_flag = 0

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to the ultrasonic ranger topic 
    client.subscribe("sonya_ethan/ultrasonicRanger")

    # subscribing to light sensor topic 
    client.subscribe("sonya_ethan/lightsensor")


# Custom callback that prints the ultrasonic ranger values
def on_ultrasonic_message(client, userdata, msg):
    alert_flag = 1
    # Convert payload to string using python string decode method
    message = msg.payload.decode("utf-8")
    # Prints the ultrasonic ranger values received from the RPi
    print("Motion has been detected - ", "Distance:", message, "cm")

def on_light_message(client, userdata, msg):
    alert_flag = 1
    # Convert payload to string using python string decode method
    message = msg.payload.decode("utf-8")
    # Prints the light sensor values received from the RPi
    print("Light has been detected ", message)

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect

    # Set custom callback for the ultrasonic ranger topic
    client.subscribe("sonya_ethan/ultrasonicRanger")
    client.message_callback_add("sonya_ethan/ultrasonicRanger", on_ultrasonic_message)

    client.subscribe("sonya_ethan/lightsensor")
    client.message_callback_add("sonya_ethan/lightsensor", on_light_message)

    client.connect(host="broker.hivemq.com", port=1883, keepalive=60)
    client.loop_start()

    while True:
        if (alert_flag):
            user_input = input("Do you approve this detection? (y/n)")
            if user_input == "y":
                client.publish("sonya_ethan/intruder_msg", "TURN_OFF_ALARMS")
            elif user_input == "n":
                client.publish("sonya_ethan/intruder_msg", "TURN_ON_ALARMS")
            else:
                print("Invalid input.")
            alert_flag = 0
        time.sleep(1)
            

