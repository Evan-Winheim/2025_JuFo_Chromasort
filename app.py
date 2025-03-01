#!/usr/bin/env python3
import os
import sys
import threading
import time
import logging
import serial
from datetime import datetime, date

from adafruit_servokit import ServoKit
import torchvision.transforms as transforms
from jetcam.usb_camera import USBCamera
import torch
import torchvision
import torch.nn.functional as F
from utils import preprocess  # Stelle sicher, dass das utils-Modul im selben Verzeichnis liegt

from flask import Flask, render_template, Response, jsonify

# ---------------------------
# Konfiguration und Flags
# ---------------------------
DEBUG_MODE = False       # True, wenn Bilder gespeichert werden sollen
MIN_PROBABILITY = 0.7    # Mindestwahrscheinlichkeit (70%)

KANAL_SERVO_1 = 0
KANAL_SERVO_2 = 15

FARBE_BLAU     = "\033[44m"
FARBE_WEISS    = "\033[47m"
FARBE_GELB     = "\033[43m"
FARBE_LEER     = "\033[40m"
FARBE_UNBEKANNT= "\033[47m"
RESET          = "\033[0m"

# ---------------------------
# Flask App und Logging
# ---------------------------
app = Flask(__name__)

log_messages = []
class ListHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_messages.append(log_entry)
        if len(log_messages) > 200:
            del log_messages[0]
list_handler = ListHandler()
list_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logging.getLogger().addHandler(list_handler)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.WARNING)  # Nur Warnungen und Fehler ausgeben
stream_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logging.getLogger().addHandler(stream_handler)


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

@app.route('/logs')
def logs():
    # Filtere alle Log-Nachrichten, die nicht "[INFO]" enthalten
    filtered_logs = [msg for msg in log_messages if "GET /" not in msg]
    # Umkehren der Reihenfolge: neueste Nachrichten zuerst
    filtered_logs.reverse()
    return jsonify({'logs': filtered_logs})


# ---------------------------
# Hardware-Initialisierung und Funktionen
# ---------------------------

# Initialisiere alle Komponenten (nun ohne Bedingung)
try:
    kit = ServoKit(channels=16)
    logging.info("ServoKit erfolgreich initialisiert.")
except Exception as e:
    logging.error("Fehler bei der Initialisierung des ServoKit: %s", e)
    sys.exit(1)

try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1, dsrdtr=True, rtscts=True)
    time.sleep(2)
    logging.info("Arduino erfolgreich initialisiert.")
except Exception as e:
    logging.error("Fehler bei der Initialisierung des Arduino: %s", e)
    sys.exit(1)

try:
    camera = USBCamera(width=224, height=224, capture_device=0)
    camera.running = True
    logging.info("USB-Kamera erfolgreich initialisiert.")
except Exception as e:
    logging.error("Fehler bei der Initialisierung der USB-Kamera: %s", e)
    sys.exit(1)

CATEGORIES = ['leer', 'weiss', 'blau', 'gelb','unbekannt']
TRANSFORMS = transforms.Compose([
    transforms.ColorJitter(0.2, 0.2, 0.2, 0.2),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logging.info("Verwende Gerät: %s", device)
try:
    model = torchvision.models.resnet18(pretrained=True)
    model.fc = torch.nn.Linear(512, len(CATEGORIES))
    model = model.to(device)
    model.eval()
    logging.info("Modell erfolgreich initialisiert.")
except Exception as e:
    logging.error("Fehler bei der Modellinitialisierung: %s", e)
    sys.exit(1)
model_path = 'my_model.pth'
try:
    model.load_state_dict(torch.load(model_path))
    logging.info("Das Klassifikation Modell wurde erfolgreich geladen.")
except FileNotFoundError:
    logging.error("Es wurde kein Klassifikation Modell gefunden. Es wird ein neues Modell verwendet.")

def draw_lego_brick():
    lego_brick = """
          __________________
         /  ( )  ( )  ( )  /|
        /  ( )  ( )  ( )  / |
       /_________________/  |
      |   Chroma Sort   |   |
      |   Evan Winheim  |  /   
      |_________________|_/
                (c) 2024
        """
    print(lego_brick)
    steuerung("leer")

def save_image(image, category):
    today = date.today().strftime("%Y-%m-%d")
    directory = f"images/{today}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    seconds_since_epoch = int(datetime.now().timestamp())
    filename = f"{directory}/{category}_{date.today().strftime('%H-%M-%S')}_{seconds_since_epoch}.jpg"
    with open(filename, 'wb') as f:
        f.write(image)

def move_servo_slowly(channel, start_angle, end_angle, step_size=1, delay=0.05):
    if start_angle < end_angle:
        for angle in range(start_angle, end_angle + 1, step_size):
            kit.servo[channel].angle = angle
            time.sleep(delay)
    else:
        for angle in range(start_angle, end_angle - 1, -step_size):
            kit.servo[channel].angle = angle
            time.sleep(delay)
    
def blink_block(block_number):
    message = f"{block_number}\n"
    ser.write(message.encode('utf-8'))
    print(f"Block {block_number} blinkt für 3 Sekunden.")

def steuerung(kategorie):
    if kategorie == "blau":           
        move_servo_slowly(channel=0, start_angle=90, end_angle=45, step_size=1, delay=0.05)    
        time.sleep(0.5)   
        blink_block(1)  
        time.sleep(3)   
        move_servo_slowly(channel=0, start_angle=45, end_angle=90, step_size=1, delay=0.05)
        time.sleep(0.5)
    elif kategorie == "weiss":                
        move_servo_slowly(channel=15, start_angle=90, end_angle=40, step_size=1, delay=0.05)    
        time.sleep(0.5)  
        blink_block(2)  
        time.sleep(3)     
        move_servo_slowly(channel=15, start_angle=45, end_angle=90, step_size=1, delay=0.05)
        time.sleep(0.5)
    elif kategorie == "gelb":            
        move_servo_slowly(channel=15, start_angle=90, end_angle=135, step_size=1, delay=0.05)
        time.sleep(0.5)
        blink_block(3)  
        time.sleep(3) 
        move_servo_slowly(channel=15, start_angle=135, end_angle=90, step_size=1, delay=0.05)
        time.sleep(0.5)
    elif kategorie == "unbekannt":                
        move_servo_slowly(channel=0, start_angle=90, end_angle=135, step_size=1, delay=0.05)    
        time.sleep(0.5)    
        blink_block(4)  
        time.sleep(3) 
        move_servo_slowly(channel=0, start_angle=135, end_angle=90, step_size=1, delay=0.05)
        time.sleep(0.5) 
        
    time.sleep(1)

current_prediction = {"category": "Noch nicht gestartet", "probability": None}
evaluation_running = True

# Funktion für die Live-Bewertung
def live_evaluation():
    global current_prediction
    while True:
        # Bild erfassen und vorverarbeiten
        image = camera.value
        preprocessed = preprocess(image).to(device)
        output = model(preprocessed)
        output = F.softmax(output, dim=1).detach().cpu().numpy().flatten()

        # Ausgabe
        category_index = output.argmax()
        max_probability = output[category_index]

        if max_probability < MIN_PROBABILITY:
            category = "unbekannt"
            logging.info("Kategorie: {CATEGORIES[category_index]} => Wahrscheinlichkeit zu niedrig ({max_probability:.2f}). Kategorie auf 'unbekannt' gesetzt.")
        else:
            logging.info("Kategorie: {CATEGORIES[category_index]}")
            for i, probability in enumerate(list(output)):
                print(f"{CATEGORIES[i]}: {probability * 100:.2f}")
            category = CATEGORIES[category_index]
    
        # Erstelle ein Dictionary mit den Wahrscheinlichkeiten als native Floats
        probs = {cat: round(float(prob) * 100, 2) for cat, prob in zip(CATEGORIES, output)}
        
        if "leer" in probs:
            del probs["leer"]
        current_prediction = {
            "category": category,
            "probability": max_probability,
            "probabilities": probs
        }
        
        # Servo-Steuerung basierend auf der Kategorie
        steuerung(category)

        # Warte vor der nächsten Auswertung
        time.sleep(1)
        
        

prediction_thread = threading.Thread(target=live_evaluation)
prediction_thread.daemon = True
prediction_thread.start()
logging.debug("Prediction-Thread gestartet.")

def gen_frames():
    while True:
        try:
            frame = camera.value
            if frame is None:
                logging.warning("Kein Frame von der Kamera empfangen.")
                continue
            from jetcam.utils import bgr8_to_jpeg
            jpeg_bytes = bgr8_to_jpeg(frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n')
            time.sleep(0.1)
        except Exception as e:
            logging.error("Fehler in gen_frames: %s", e)
            time.sleep(0.1)

@app.route('/')
def index():
    logging.info("Index-Seite wurde aufgerufen.")
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    logging.debug("Video-Feed angefragt.")
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/prediction')
def prediction():
    logging.debug("Prediction abgefragt: %s", current_prediction)
    pred = {
        "category": current_prediction["category"],
        "probability": float(current_prediction["probability"]) if current_prediction["probability"] is not None else None,
        "probabilities": current_prediction.get("probabilities", {})
    }
    return jsonify({'prediction': pred})

if __name__ == '__main__':
    logging.info("Starte Flask-App auf 0.0.0.0:5000")
    #app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
