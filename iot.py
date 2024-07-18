import cv2
from ultralytics import YOLO
import pytesseract
from datetime import datetime as dt
import time
import re
import numpy as np
import paho.mqtt.client as mqtt
import csv
import subprocess
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Successful Connection")

def on_message(client, userdata, msg):
    print("Received data:" + msg.topic + '->' + msg.payload.decode("utf-8"))

def send_trigger_signal(result):
    # Raspberry Pi code
    print(f"{result} detected, gate open")

model = YOLO('license_plate_detector.pt')
next_available_slot = (0, 0)
counter = 0
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # width
cap.set(4, 480)  # height
min_area = 500
count = 0
regex = re.compile(r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$')

# MQTT Configuration
broker = "332033224b2f4f209adc7ec77250f4e0.s1.eu.hivemq.cloud"
username = "admin"
pwd = "Mukundh1703."
topic = 'testtopic/anpr'
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(username, pwd)
client.connect(broker, 8883)
parking_space = np.zeros((10, 10))  # Initialize parking space matrix in each iteration


# Function to write parking_space matrix to CSV file
def write_parking_space_to_csv(matrix, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(matrix)

while True:
    success, img = cap.read()

    if not success:
        print("Failed to capture image.")
        continue

    results = model.predict(img, show=True)
    boxes = results[0].boxes.xyxy.tolist()
    classes = results[0].boxes.cls.tolist()
    names = results[0].names
    confidences = results[0].boxes.conf.tolist()


    for box, cls, conf in zip(boxes, classes, confidences):
        x1, y1, x2, y2 = box
        confidence = conf
        detected_class = cls
        name = names[int(cls)]

        if conf >= 0.71:
            img_roi = img[int(y1):int(y2), int(x1): int(x2)]  # crop function
            gray = cv2.cvtColor(img_roi, cv2.COLOR_BGR2GRAY)
            gray = cv2.bilateralFilter(gray, 11, 17, 17)
            result = pytesseract.image_to_string(gray, config='--psm 7', lang='eng').replace('\n\x0c', '').replace(' ', '').replace('\n', "")
            print(f'{result} , {result.isalnum()}')
            if result.isalnum() and regex.match(result):
                # Find the next available parking slot
                i, j = next_available_slot
                while parking_space[i][j] != 0:
                    j += 1
                    if j >= 10:
                        j = 0
                        i += 1
                        if i >= 10:
                            break

                if i < 10 and j < 10:
                    slot_number = i * 10 + j + 1
                    parking_space[i][j] = 1  # Mark the slot as occupied
                    send_trigger_signal(result)
                    current_time = dt.now()
                    current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
                    data=f"Slot {slot_number} booked for Vehicle number:{result} , at {current_time_str} , you will be charged Rs.50/hr"
                    client.publish(topic, data)
                    subprocess.call(["say",f"Please proceed to slot {slot_number} , Row {i+1} , Space {j+1}, you will be charged Rupees 50 per hour, thank you for your patience"])
                    time.sleep(10)

    # Write parking_space matrix to CSV file
    write_parking_space_to_csv(parking_space, 'parking_space.csv')

    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.waitKey(100)
        count += 1
    counter += 1
