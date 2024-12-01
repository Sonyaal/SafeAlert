# Detects motion, triggers Buzzer, and LED

import grovepi
import time


led_port = 3 # D3
buzzer = 4 # D4
# Connect the Grove Ultrasonic Ranger to digital port D2
ultrasonic_ranger = 2 # D2

# Initialize the LED as an output
grovepi.pinMode(led_port, "OUTPUT")

# Custom callback for LED control
def on_led_message(client, userdata, msg):
    message = msg.payload.decode("utf-8")
    if message == "LED_ON":
        print("Turning LED on")
        # Turning LED on 
        grovepi.digitalWrite(led_port, 1)
    elif message == "LED_OFF": # this message would be sent if user decides to turn off alarm
        print("Turning LED off")
        # Turning LED off
        grovepi.digitalWrite(led_port, 0) 
    else:
        # Error handling if we don't get an expected message
        print("Received unknown message:", message)

# Custom callback for buzzer control
def on_led_message(client, userdata, msg):
    message = msg.payload.decode("utf-8")
    if message == "BUZZER_ON":
        print("Turning BUZZER on")
        # Turning LED on 
        grovepi.analogWrite(buzzer, 100) 
    elif message == "BUZZER_OFF":
        print("Turning BUZZER off")
        # Turning LED off
        grovepi.analogWrite(buzzer, 0) 
    else:
        # Error handling if we don't get an expected message
        print("Received unknown message:", message)

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to topics of interest here
    client.subscribe("sonya_ethan/led")
    client.subscribe("sonya_ethan/buzzer")

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

def alert():
    grovepi.analogWrite(buzzer, 100) # Make a sound on the Buzzer
    grovepi.digitalWrite(led_port, 1)  # Turn on the status LED to indicate the detection

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect

    # Set custom callback for the LED topic
    client.message_callback_add("sonya_ethan/led", on_led_message)

    client.message_callback_add("sonya_ethan/buzzer", on_lcd_message)

    client.connect(host="broker.hivemq.com", port=1883, keepalive=60)
    client.loop_start()


    while True:     # in case of IO error, restart
        try:
            while True:
                # Read the ultrasonic ranger value
                distance = grovepi.ultrasonicRead(ultrasonic_ranger)        
                # Eventually include a check for sound being detected (we need two sensors)

                if distance < 100:  # If a person walks through the door
                    print("ALERT - motion has been detected") # Can print this to the lcd too if we are feelin fancy 
                    alert()
                    # Publish the distance to the ultrasonicRanger topic
                    client.publish("sonya_ethan/ultrasonicRanger", str(distance)) # signals motion has been detected
                    print("Published distance:", distance, "cm")
                    # This dectection is going to cause a change on the webpage that alerts the user and 
                    # prompts them to make a decision on if they should diffuse the alarm
                        # OOH we could make the user type in a password to turn on the alarm... thats like a digital signature right...? 

                # Same logic will occur for the noise detector

                # I'm thinking we continue to make the buzzer sound until we get a message back that the user
                # is approves this decection (same goes for the LED)

                if () { # message has been recieved that says the motion is okay, turn off all outputs / maybe could timeout after a certain point?
                    grovepi.analogWrite(buzzer,0)       # Turn off the Buzzer
                    grovepi.digitalWrite(led_port,0)  # Turn off the LED
                }

    except IOError:
        print("Error")