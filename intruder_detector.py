# Detects motion, triggers Buzzer, and LED

import grovepi
import time


led_status = 3 # D3
buzzer = 4 # D4
# Connect the Grove Ultrasonic Ranger to digital port D2
ultrasonic_ranger = 2

while True:     # in case of IO error, restart
    try:
        grovepi.pinMode(switch,"INPUT")
        while True:
                    # Eventually include a check for sound being detected (we need two sensors)
                    if grovepi.ultrasonicRead(ultrasonic_ranger) < 100 :  # If a person walks through the door
                    print("ALERT - motion has been detected") # Can print this to the lcd too if we are feelin fancy 

                    # Publish the distance to the ultrasonicRanger topic with the message that there has been an intruder
                        # look at rpi_pub_and_sub for an example!!
                        # This dectection is going to cause a change on the webpage that alerts the user and 
                        # prompts them to make a decision on if they should diffuse the alarm
                            # OOH we could make the user type in a password to turn on the alarm... thats like a digital signature right...? 

                    # I'm thinking we continue to make the buzzer sound until we get a message back that the user
                    # is approves this decection (same goes for the LED)
                    grovepi.analogWrite(buzzer,300) # Make a sound on the Buzzer
                    grovepi.digitalWrite(led_status,1)  # Turn on the status LED to indicate that someone has arrived

                    if () { # message has been recieved that says the motion is okay, turn off all outputs / maybe could timeout after a certain point?
                        grovepi.analogWrite(buzzer,0)       # Turn off the Buzzer
                        grovepi.digitalWrite(led_status,0)  # Turn off the LED
                    }

    except IOError:
        print("Error")