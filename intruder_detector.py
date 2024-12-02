# Detects motion, triggers Buzzer, and LED

import grovepi
import time
import paho.mqtt.client as mqtt

led_port = 3 # D3
buzzer_port = 4 # D4
ultrasonic_ranger_port = 2 # D2
# light_sensor_port = 0  # A0

# Initialize the LED as an output
grovepi.pinMode(led_port, "OUTPUT")
# Initialize the buzzer as an output
grovepi.pinMode(buzzer_port, "OUTPUT")

# Initialize the ultrasonic ranger as input
grovepi.pinMode(ultrasonic_ranger_port, "INPUT")
# Initialize the light sensor as input
# grovepi.pinMode(light_sensor_port, "INPUT")

light_threshold = 250  
distance_threshold = 100
alert_flag = 0
user_response = 0 

# # Custom callback for LED control
# def on_led_message(client, userdata, msg):
#     message = msg.payload.decode("utf-8")
#     if message == "LED_ON":
#         print("Turning LED on")
#         # Turning LED on 
#         grovepi.digitalWrite(led_port, 1)
#     elif message == "LED_OFF": # this message would be sent if user decides to turn off alarm
#         print("Turning LED off")
#         # Turning LED off
#         grovepi.digitalWrite(led_port, 0) 
#     else:
#         # Error handling if we don't get an expected message
#         print("Received unknown message:", message)

# # Custom callback for buzzer control
# def on_led_message(client, userdata, msg):
#     message = msg.payload.decode("utf-8")
#     if message == "BUZZER_ON":
#         print("Turning BUZZER on")
#         # Turning LED on 
#         grovepi.analogWrite(buzzer, 100) 
#     elif message == "BUZZER_OFF":
#         print("Turning BUZZER off")
#         # Turning LED off
#         grovepi.analogWrite(buzzer_port, 0) 
#     else:
#         # Error handling if we don't get an expected message
#         print("Received unknown message:", message)

# RPI will only be recieving messages from the user on this topic
def on_intruder_message(client, userdata, msg):
    message = msg.payload.decode("utf-8")
    user_response = 1
    if message == "TURN_OFF_ALARMS": # sent when user wants to disable alarms
        print("Turning alarms off")
        disable_alarms()
    elif message == "TURN_ON_ALARMS": # sent when user wants to keep alarms on ???
        print("Turning alarms on")
        alert()
    else:
        # Error handling if we don't get an expected message
        print("Received unknown message:", message)

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to topics of interest here
    # client.subscribe("sonya_ethan/led")
    # client.subscribe("sonya_ethan/buzzer")
    client.subscribe("sonya_ethan/intruder_msg")

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

def alert():
    grovepi.analogWrite(buzzer_port, 100) # Make a sound on the Buzzer
    grovepi.digitalWrite(led_port, 1)  # Turn on the status LED to indicate the detection

def disable_alarms():
    grovepi.analogWrite(buzzer_port, 0) # Turn off buzzer
    grovepi.digitalWrite(led_port, 0)  # Turn off red led

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect

    # # Set custom callback for the LED topic
    # client.message_callback_add("sonya_ethan/led", on_led_message)

    # # Set custom callback for the BUZZER topic
    # client.message_callback_add("sonya_ethan/buzzer", on_lcd_message)

    # Set custom callback for the both outputs (buzzer and light)
    client.message_callback_add("sonya_ethan/intruder_msg", on_intruder_message)

    client.connect(host="broker.hivemq.com", port=1883, keepalive=60)
    client.loop_start()


    while True:     # in case of IO error, restart
        try:
            while True:
                # Read the ultrasonic ranger value
                distance = grovepi.ultrasonicRead(ultrasonic_ranger_port)  
                print("Distance: ", distance)  
                # light_level = grovepi.analogRead(light_sensor_port)
                # print("Light level: ", light_level)      
                # Eventually include a check for sound being detected (we need two sensors)

                if distance > distance_threshold:  # If a person walks through the door
                    print("ALERT - motion has been detected")
                    alert()
                    # Publish the distance to the ultrasonicRanger topic
                    client.publish("sonya_ethan/ultrasonicRanger", str(distance)) # signals motion has been detected
                    print("Published distance:", distance, "cm")
                    # This dectection is going to cause a change on the webpage that alerts the user and 
                    # prompts them to make a decision on if they should diffuse the alarm
                        # OOH we could make the user type in a password to turn on the alarm... thats like a digital signature right...? 
                # elif light_level > light_threshold:
                #     print("ALERT - light has been detected")
                #     alert()
                #     # Publish the light level to the lightsensor topic
                #     client.publish("sonya_ethan/lightsensor", str(light_level)) # signals light has been detected
                #     print("Published light level:", light_level)

                    # This dectection is going to cause a change on the webpage that alerts the user and 
                    # prompts them to make a decision on if they should diffuse the alarm
                        # OOH we could make the user type in a password to turn on the alarm... thats like a digital signature right...? 
                if (alert_flag):
                    buzzer_val = 100
                    # Make buzzer noise increase while the user has not responded
                    while user_response == 0:
                        buzzer_val = buzzer_val + 10
                        grovepi.analogWrite(buzzer_port, buzzer_val)
                        time.sleep(1)
                    if (user_response):
                        # setting flag back to 0
                        user_response = 0 
                time.sleep(10)

        except IOError:
            print("Error")
