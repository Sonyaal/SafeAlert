import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

class IoTDashboard:

    def __init__(self, root):
        self.root = root
        self.root.title("IoT Dashboard")
        self.root.geometry("800x700")
        self.alert_flag = False

        # Background
        self.root.configure(bg="#1F1F1F")

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
        self.alert_label = tk.Label(root, text="Secure", font=("Arial", 48, "bold"),
                                    fg="green", bg="#1F1F1F")
        self.alert_label.pack(pady=0)

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

        # Set up MQTT Client
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect

        self.client.message_callback_add("sonya_ethan/ultrasonicRanger", self.on_ultrasonic_message)
        self.client.message_callback_add("sonya_ethan/lightsensor", self.on_light_message)

        self.client.connect("broker.emqx.io", 1883, 60)
        self.client.username_pw_set(username="your_username", password="your_password")

        # Start MQTT loop
        self.client.loop_start()

    def decrypt_message(self, encrypted_message, private_key_pem):
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        decrypted_message = private_key.decrypt(
            encrypted_message,
            padding.OAEP(  # Ensure this is the correct OAEP from asymmetric.padding
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_message.decode()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to broker with result code", rc)
        client.subscribe("sonya_ethan/ultrasonicRanger")
        client.subscribe("sonya_ethan/lightsensor")

    def on_ultrasonic_message(self, client, userdata, msg):
        encrypted_message = msg.payload
        private_key_path = "private_key.pem"
        with open(private_key_path, "rb") as f:
            private_key_pem = f.read()

        try:
            decrypted_message = self.decrypt_message(encrypted_message, private_key_pem)
            print("Decrypted ultrasonic message:", decrypted_message)
            self.ultrasonic_label.config(text=f"Ultrasonic Ranger: {decrypted_message} cm")
            self.set_alert("Motion detected!")
            self.alert_label.config(fg="red")
        except Exception as e:
            print("Error decrypting ultrasonic message:", e)

    def on_light_message(self, client, userdata, msg):
        encrypted_message = msg.payload
        private_key_path = "private_key.pem"
        with open(private_key_path, "rb") as f:
            private_key_pem = f.read()

        try:
            decrypted_message = self.decrypt_message(encrypted_message, private_key_pem)
            print("Decrypted light message:", decrypted_message)
            self.light_label.config(text=f"Light Sensor: {decrypted_message}")
            self.set_alert("Light detected!")
            self.alert_label.config(fg="red")
        except Exception as e:
            print("Error decrypting light message:", e)

    #Default message callback. Please use custom callbacks.
    def on_message(client, userdata, msg):
        print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

    def handle_alert(self, alert_text):
        self.alert_label.config(text=alert_text)
        self.enable_buttons()

    def enable_buttons(self):
        self.yes_button.config(state="normal")
        self.no_button.config(state="normal")

    def disable_buttons(self):
        self.yes_button.config(state="disabled")
        self.no_button.config(state="disabled")

    def approve_detection(self):
        self.client.publish("sonya_ethan/intruder_msg", "TURN_OFF_ALARMS")
        self.status_label.config(text="Detection Approved")
        self.set_alert("Secure.")
        self.alert_label.config(fg="green")
        self.disable_buttons()

    def reject_detection(self):
        self.client.publish("sonya_ethan/intruder_msg", "KEEP_ALARMS_ON")
        self.status_label.config(text="Detection Rejected")
        self.set_alert("Secure.")
        self.alert_label.config(fg="green")
        self.disable_buttons()
    
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

if __name__ == "__main__":
    root = tk.Tk()
    dashboard = IoTDashboard(root)
    root.mainloop()
