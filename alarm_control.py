import tkinter as tk
from tkinter import ttk
# from paho.mqtt.client import Client
import threading
import random

class IoTDashboard:

    # This is the UI code for the dashboard. Elements are defined top to bottom on the window.
    def __init__(self, root):
        self.root = root
        self.root.title("IoT Dashboard")
        self.root.geometry("800x700")
        self.alert_flag = False

        # Background
        self.root.configure(bg="#1F1F1F")

        spacer = tk.Label(root, bg="#1F1F1F")
        spacer.pack(pady=20)
        
        # Logo
        logo_label = tk.Label(root, text="SafeAlert", font=("Arial", 150, "bold"), fg="white", bg="#1F1F1F")
        logo_label.pack(pady=0)
        
        # By Sonya and Ethan
        logo_label = tk.Label(root, text="By Sonya and Ethan", font=("Arial", 16, "normal"), fg="white", bg="#1F1F1F")
        logo_label.pack(pady=0)

        # Spacing
        spacer = tk.Label(root, bg="#1F1F1F")
        spacer.pack(pady=5)

        # White line
        canvas = tk.Canvas(root, height=2, bg="#1F1F1F", bd=0, highlightthickness=0)
        canvas.pack(fill="x", pady=10)
        canvas.create_line(0, 1, 10000, 1, fill="white")

        # Spacing
        spacer = tk.Label(root, bg="#1F1F1F")
        spacer.pack(pady=2)

        # Red alert text
        self.alert_label = tk.Label(root, text="", font=("Arial", 48, "bold"),
                                    fg="#E74C3C", bg="#1F1F1F")
        self.alert_label.pack(pady=0)

        # Spacing
        spacer = tk.Label(root, bg="#1F1F1F")
        spacer.pack(pady=2) 

        # Action buttons frame
        self.action_frame = tk.Frame(root, bg="#1F1F1F")
        self.action_frame.pack(pady=0)

        # Approve/Deny buttons (side-by-side)
        self.yes_button = tk.Button(self.action_frame, text="Approve Detection",
                                    command=self.approve_detection,
                                    font=("Arial", 20, "bold"),
                                    bg="#A9DFBF", fg="green", relief="raised", bd=2, padx=20, pady=10)
        self.no_button = tk.Button(self.action_frame, text="Reject Detection",
                                   command=self.reject_detection,
                                   font=("Arial", 20, "bold"),
                                   bg="#FADBD8", fg="red", relief="raised", bd=2, padx=20, pady=10)
        self.yes_button.grid(row=0, column=0, padx=20, pady=10)
        self.no_button.grid(row=0, column=1, padx=20, pady=10)

        # Status indicator text
        self.status_label = tk.Label(root, text="Status: Waiting for data...",
                                     font=("Arial", 18, "bold"), bg="#1F1F1F", fg="white")
        self.status_label.pack(pady=15)

        # Diagnostic values at the bottom
        labels_frame = tk.Frame(root, bg="#1F1F1F")
        labels_frame.pack(pady=10)
        self.ultrasonic_label = tk.Label(labels_frame, text="Ultrasonic Ranger: Not yet received",
                                        font=("Arial", 14), bg="#1F1F1F", fg="#ECF0F1")
        self.ultrasonic_label.grid(row=0, column=0, padx=20, pady=10)

        self.light_label = tk.Label(labels_frame, text="Light Sensor: Not yet received",
                                    font=("Arial", 14), bg="#1F1F1F", fg="#ECF0F1")
        self.light_label.grid(row=0, column=1, padx=20, pady=10)

        # Disable buttons
        self.disable_buttons()

        # # Set up MQTT Client
        # self.client = Client()
        # self.client.on_message = self.on_message
        # self.client.on_connect = self.on_connect

        # self.client.message_callback_add("sonya_ethan/ultrasonicRanger", self.on_ultrasonic_message)
        # self.client.message_callback_add("sonya_ethan/lightsensor", self.on_light_message)

        # self.client.connect("broker.hivemq.com", 1883, 60)

        # # Run MQTT in a separate thread
        # self.mqtt_thread = threading.Thread(target=self.start_mqtt_loop, daemon=True)
        # self.mqtt_thread.start()

        # Simulated data
        self.start_test_data_simulation()

    # def start_mqtt_loop(self):
    #     self.client.loop_forever()

    # def on_connect(self, client, userdata, flags, rc):
    #     print("Connected to broker with result code", rc)
    #     client.subscribe("sonya_ethan/ultrasonicRanger")
    #     client.subscribe("sonya_ethan/lightsensor")

    # def on_ultrasonic_message(self, client, userdata, msg):
    #     message = msg.payload.decode("utf-8")
    #     self.ultrasonic_label.config(text=f"Ultrasonic Ranger: {message} cm")
    #     self.set_alert("Motion detected! Distance: " + message)

    # def on_light_message(self, client, userdata, msg):
    #     message = msg.payload.decode("utf-8")
    #     self.light_label.config(text=f"Light Sensor: {message}")
    #     self.set_alert("Light detected!")

    # def on_message(self, client, userdata, msg):
    #     print(f"Received {msg.payload.decode('utf-8')} from {msg.topic}")

    def approve_detection(self):
        # self.client.publish("sonya_ethan/intruder_msg", "TURN_OFF_ALARMS")
        self.reset_alert("Detection approved. Alarm turned off.")
    def reject_detection(self):
        # self.client.publish("sonya_ethan/intruder_msg", "TURN_ON_ALARMS")
        self.reset_alert("Detection rejected. Alarm turned on.")


    # UI state management stuff
    def set_alert(self, alert_message):
        self.alert_label.config(text=alert_message)
        self.status_label.config(text="Status: Waiting for your input...")
        self.alert_flag = True
        self.enable_buttons()
    def reset_alert(self, status_message):
        self.status_label.config(text=f"Status: {status_message}")
        self.alert_label.config(text="Secure!")
        self.alert_label.config(fg="green")
        self.alert_flag = False
        self.disable_buttons()
    def enable_buttons(self):
        self.yes_button.config(state="normal")
        self.no_button.config(state="normal")
    def disable_buttons(self):
        self.yes_button.config(state="disabled")
        self.no_button.config(state="disabled")


    # Sending random values rn in these three functions. Will eventually delete

    def start_test_data_simulation(self):
        """Continuously simulate test data for the dashboard."""
        self.simulate_ultrasonic_message()
        self.simulate_light_message()
    def simulate_ultrasonic_message(self):
        """Simulates an ultrasonic sensor message at regular intervals."""
        distance = random.randint(50, 200)
        self.ultrasonic_label.config(text=f"Ultrasonic Ranger: {distance} cm")
        self.set_alert(f"Motion detected!")
        self.alert_label.config(fg="red")
        self.root.after(3000, self.simulate_ultrasonic_message)
    def simulate_light_message(self):
        """Simulates a light sensor message at regular intervals."""
        light_level = random.choice(["Bright", "Dim", "Dark"])
        self.light_label.config(text=f"Light Sensor: {light_level}")
        self.set_alert("Light detected!")
        self.alert_label.config(fg="red")
        self.root.after(5000, self.simulate_light_message)


# Just the main function. Yk the vibes down here. Chillin as always.
if __name__ == "__main__":
    root = tk.Tk()
    dashboard = IoTDashboard(root)
    root.mainloop()





# Code that was in this file before:



# import paho.mqtt.client as mqtt
# import time

# alert_flag = 0

# def on_connect(client, userdata, flags, rc):
#     print("Connected to server (i.e., broker) with result code "+str(rc))

#     #subscribe to the ultrasonic ranger topic 
#     client.subscribe("sonya_ethan/ultrasonicRanger")

#     # subscribing to light sensor topic 
#     client.subscribe("sonya_ethan/lightsensor")


# # Custom callback that prints the ultrasonic ranger values
# def on_ultrasonic_message(client, userdata, msg):
#     alert_flag = 1
#     # Convert payload to string using python string decode method
#     message = msg.payload.decode("utf-8")
#     # Prints the ultrasonic ranger values received from the RPi
#     print("Motion has been detected - ", "Distance:", message, "cm")

# def on_light_message(client, userdata, msg):
#     alert_flag = 1
#     # Convert payload to string using python string decode method
#     message = msg.payload.decode("utf-8")
#     # Prints the light sensor values received from the RPi
#     print("Light has been detected ", message)

# #Default message callback. Please use custom callbacks.
# def on_message(client, userdata, msg):
#     print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

# if __name__ == '__main__':
#     #this section is covered in publisher_and_subscriber_example.py
#     client = mqtt.Client()
#     client.on_message = on_message
#     client.on_connect = on_connect

#     # Set custom callback for the ultrasonic ranger topic
#     client.subscribe("sonya_ethan/ultrasonicRanger")
#     client.message_callback_add("sonya_ethan/ultrasonicRanger", on_ultrasonic_message)

#     client.subscribe("sonya_ethan/lightsensor")
#     client.message_callback_add("sonya_ethan/lightsensor", on_light_message)

#     client.connect(host="broker.hivemq.com", port=1883, keepalive=60)
#     client.loop_start()

#     while True:
        
#         if (alert_flag):
#             user_input = input("Do you approve this detection? (y/n)")
#             if user_input == "y":
#                 client.publish("sonya_ethan/intruder_msg", "TURN_OFF_ALARMS")
#             elif user_input == "n":
#                 client.publish("sonya_ethan/intruder_msg", "TURN_ON_ALARMS")
#             else:
#                 print("Invalid input.")
#             alert_flag = 0

#         time.sleep(1000)
