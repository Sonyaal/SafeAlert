import grovepi
import time
import paho.mqtt.client as mqtt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

led_port = 3  # D3
buzzer_port = 4  # D4
ultrasonic_ranger_port = 2  # D2
light_sensor_port = 0  # A0

# Initialize the LED as an output
grovepi.pinMode(led_port, "OUTPUT")
# Initialize the buzzer as an output
grovepi.pinMode(buzzer_port, "OUTPUT")

# Initialize the ultrasonic ranger as input
grovepi.pinMode(ultrasonic_ranger_port, "INPUT")
# Initialize the light sensor as input
grovepi.pinMode(light_sensor_port, "INPUT")

light_threshold =   100
distance_threshold = 100

# Load the public key
with open("public_key.pem", "rb") as f:
    public_key_pem = f.read()

def encrypt_message(message, public_key_pem):
    public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
    
    encrypted_message = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return encrypted_message

def on_intruder_message(client, userdata, msg):
    global user_response
    message = msg.payload.decode("utf-8")
    user_response = 1
    if message == "TURN_OFF_ALARMS":
        print("Turning alarms off")
        disable_alarms()
    elif message == "KEEP_ALARMS_ON":
        print("Keeping alarms on")
        alert()
    else:
        print("Received unknown message:", message)

def on_connect(client, userdata, flags, rc):
    print("Connected to server with result code "+str(rc))
    client.subscribe("sonya_ethan/intruder_msg")

def alert():
    grovepi.analogWrite(buzzer_port, 120)  # Make a sound on the Buzzer
    grovepi.digitalWrite(led_port, 1)  # Turn on the status LED to indicate the detection

def disable_alarms():
    global user_response
    print("in disable_alarms")
    grovepi.analogWrite(buzzer_port, 0)  # Turn off buzzer
    grovepi.digitalWrite(led_port, 0)  # Turn off red led

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))


if __name__ == '__main__':
    alert_flag = 0
    user_response = 0
    # Initialize both outputs to off
    grovepi.analogWrite(buzzer_port, 0)  # Turn off buzzer
    grovepi.digitalWrite(led_port, 0)  # Turn off red led

    # Set up MQTT protocol
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.message_callback_add("sonya_ethan/intruder_msg", on_intruder_message)

    client.connect(host="broker.emqx.io", port=1883, keepalive=60)
    client.username_pw_set(username="your_username", password="your_password")
    client.loop_start()

    while True:
        try:
            while True:
                distance = grovepi.ultrasonicRead(ultrasonic_ranger_port)
                print("Distance: ", distance)
                light_level = grovepi.analogRead(light_sensor_port)
                print("Light level: ", light_level)

                if distance < distance_threshold:
                    alert_flag = 1
                    print("ALERT - motion has been detected")
                    alert()
                    encrypted_message = encrypt_message(str(distance), public_key_pem)
                    client.publish("sonya_ethan/ultrasonic_ranger", encrypted_message)
                    print("Published encrypted distance:", encrypted_message)

                elif light_level > light_threshold:
                    alert_flag = 1
                    print("ALERT - light has been detected")
                    alert()
                    encrypted_message = encrypt_message(str(light_level), public_key_pem)
                    client.publish("sonya_ethan/light_sensor", encrypted_message)
                    print("Published encrypted light level:", encrypted_message)

                if (alert_flag):
                    buzzer_val = 120
                    while user_response == 0:
                        buzzer_val = buzzer_val + 10
                        grovepi.analogWrite(buzzer_port, buzzer_val)
                        time.sleep(1)
                    if (user_response):
                        user_response = 0
                    alert_flag = 0
                time.sleep(1)

        except IOError:
            print("Error")
