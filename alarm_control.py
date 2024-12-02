import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import padding
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

        # Spacing
        spacer = tk.Label(root, bg="#1F1F1F")
        spacer.pack(pady=20)

        # Red alert text
        self.alert_label = tk.Label(root, text="", font=("Arial", 48, "bold"),
                                    fg="#E74C3C", bg="#1F1F1F")
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
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_message.decode()

    def poll_mqtt(self):
        self.client.loop(timeout=1.0)  # Process MQTT messages
        self.root.after(100, self.poll_mqtt)  # Poll again after 100ms

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
            self.ultrasonic_label.config(text="Ultrasonic Ranger: " + decrypted_message)
            self.handle_alert("Motion Detected")
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
            self.light_label.config(text="Light Sensor: " + decrypted_message)
            self.handle_alert("Light Detected")
        except Exception as e:
            print("Error decrypting light message:", e)

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
        self.alert_label.config(text="Detection Approved")
        self.disable_buttons()

    def reject_detection(self):
        self.alert_label.config(text="Detection Rejected")
        self.disable_buttons()

if __name__ == "__main__":
    root = tk.Tk()
    dashboard = IoTDashboard(root)
    dashboard.poll_mqtt()
    root.mainloop()
