# Detects motion, triggers Buzzer, and LED

import grovepi
import time
import paho.mqtt.client as mqtt

led_port = 3 # D3
buzzer_port = 4 # D4
ultrasonic_ranger_port = 2 # D2
light_sensor_port = 0  # A0

# Initialize the LED as an output
grovepi.pinMode(led_port, "OUTPUT")
# Initialize the buzzer as an output
grovepi.pinMode(buzzer_port, "OUTPUT")

# Initialize the ultrasonic ranger as input
grovepi.pinMode(ultrasonic_ranger_port, "INPUT")
# Initialize the light sensor as input
grovepi.pinMode(light_sensor_port, "INPUT")

light_threshold = 250  
distance_threshold = 100

# RPI will only be recieving messages from the user on this topic
def on_intruder_message(client, userdata, msg):
    global user_response  # Declare user_response as global
    message = msg.payload.decode("utf-8")
    user_response = 1
    if message == "TURN_OFF_ALARMS": # sent when user wants to disable alarms
        print("Turning alarms off")
        disable_alarms()
    elif message == "KEEP_ALARMS_ON": # sent when user wants to keep alarms on ???
        print("Keeping alarms on")
        alert()
    else:
        # Error handling if we don't get an expected message
        print("Received unknown message:", message)

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to topics of interest here
    client.subscribe("sonya_ethan/intruder_msg")

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

def alert():
    grovepi.analogWrite(buzzer_port, 120) # Make a sound on the Buzzer
    grovepi.digitalWrite(led_port, 1)  # Turn on the status LED to indicate the detection

def disable_alarms():
    global user_response  # Declare user_response as global
    print("in disable_alarms")
    print("user response is", user_response)
    grovepi.analogWrite(buzzer_port, 0) # Turn off buzzer
    grovepi.digitalWrite(led_port, 0)  # Turn off red led

if __name__ == '__main__':

    alert_flag = 0
    user_response = 0

    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect

    # Set custom callback for the both outputs (buzzer and light)
    client.message_callback_add("sonya_ethan/intruder_msg", on_intruder_message)

    client.connect(host="broker.emqx.io", port=1883, keepalive=60)
    client.username_pw_set(username="your_username", password="your_password")
    client.loop_start()


    while True:     # in case of IO error, restart
        try:
            while True:
                # Read the ultrasonic ranger value
                distance = grovepi.ultrasonicRead(ultrasonic_ranger_port)  
                print("Distance: ", distance)  
                light_level = grovepi.analogRead(light_sensor_port)
                print("Light level: ", light_level)      

                if distance < distance_threshold:  # If a person walks through the door
                    alert_flag = 1
                    print("ALERT - motion has been detected")
                    alert()
                    # Publish the distance to the ultrasonicRanger topic
                    client.publish("sonya_ethan/ultrasonicRanger", str(distance)) # signals motion has been detected
                    print("Published distance:", distance, "cm")
                    # This dectection is going to cause a change on the webpage that alerts the user and 
                    # prompts them to make a decision on if they should diffuse the alarm
                        # OOH we could make the user type in a password to turn on the alarm... thats like a digital signature right...? 
                elif light_level > light_threshold:
                    alert_flag = 1
                    print("ALERT - light has been detected")
                    alert()
                    # Publish the light level to the lightsensor topic
                    client.publish("sonya_ethan/lightsensor", str(light_level)) # signals light has been detected
                    print("Published light level:", light_level)

                if (alert_flag):
                    buzzer_val = 100
                    # Make buzzer noise increase while the user has not responded
                    while user_response == 0:
                        print("in while loop")
                        print("buzzer value: ", buzzer_val)
                        # buzzer_val = 120
                        # grovepi.analogWrite(buzzer_port, buzzer_val)
                        time.sleep(1)
                    if (user_response):
                        # setting flag back to 0
                        user_response = 0 
                    alert_flag = 0
                time.sleep(1)

        except IOError:
            print("Error")
