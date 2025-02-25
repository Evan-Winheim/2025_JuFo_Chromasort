# sudo LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1 python3.6 chromasort.py

import os
import time
from datetime import datetime
from datetime import date

from adafruit_servokit import ServoKit

import torchvision.transforms as transforms
from jetcam.usb_camera import USBCamera
import torch
import torchvision
import torch.nn.functional as F
from utils import preprocess  # Stellen Sie sicher, dass das utils-Modul im selben Verzeichnis wie Ihr Skript liegt

# Debug-Flag: Wenn True, werden Bilder gespeichert
DEBUG_MODE = False  # True oder False

# Konfiguration für Mindestwahrscheinlichkeit
MIN_PROBABILITY = 0.7  # Mindestwahrscheinlichkeit (70%)

# Konstanten für Servokanäle
KANAL_SERVO_1 = 0       # Kanal auf dem PCA9685
KANAL_SERVO_2 = 15      # Kanal auf dem PCA9685

# Initialisiere ServoKit für PCA9685 mit 16 Kanälen
kit = ServoKit(channels=16)

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

# Funktion zum Speichern der Bilder
def save_image(image, category):
    today = date.today().strftime("%Y-%m-%d")
    directory = f"images/{today}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    seconds_since_epoch = int(datetime.now().timestamp())  # Sekunden seit der Epoch erhalten
    filename = f"{directory}/{category}_{date.today().strftime('%H-%M-%S')}_{seconds_since_epoch}.jpg"
    with open(filename, 'wb') as f:
        f.write(image)

# Funktion, um den Servo langsam zu bewegen
def move_servo_slowly(channel, start_angle, end_angle, step_size=1, delay=0.05):
    # Bewege den Servo schrittweise von start_angle zu end_angle
    if start_angle < end_angle:
        for angle in range(start_angle, end_angle + 1, step_size):
            kit.servo[channel].angle = angle
            time.sleep(delay)
    else:
        for angle in range(start_angle, end_angle - 1, -step_size):
            kit.servo[channel].angle = angle
            time.sleep(delay)

# Funktion zum Steuern der Servos
def steuerung(kategorie):
    """
    Steuert die Servomotoren basierend auf der Kategorie.

    Parameter:
    kategorie (str): Die Kategorie ("blau", "weiß", "gelb", "unbekannt").
    """
    if kategorie == "blau":        
        move_servo_slowly(channel=0, start_angle=90, end_angle=45, step_size=1, delay=0.05)    
        time.sleep(0.5)    
        move_servo_slowly(channel=0, start_angle=45, end_angle=90, step_size=1, delay=0.05)
        time.sleep(0.5)

    elif kategorie == "weiss":        
        move_servo_slowly(channel=15, start_angle=90, end_angle=45, step_size=1, delay=0.05)    
        time.sleep(0.5)    
        move_servo_slowly(channel=15, start_angle=45, end_angle=90, step_size=1, delay=0.05)
        time.sleep(0.5)

    elif kategorie == "gelb":        
        move_servo_slowly(channel=15, start_angle=90, end_angle=135, step_size=1, delay=0.05)
        time.sleep(0.5)
        move_servo_slowly(channel=15, start_angle=135, end_angle=90, step_size=1, delay=0.05)

    elif kategorie == "unbekannt":        
        move_servo_slowly(channel=0, start_angle=90, end_angle=135, step_size=1, delay=0.05)    
        time.sleep(0.5)    
        move_servo_slowly(channel=0, start_angle=135, end_angle=90, step_size=1, delay=0.05)
        time.sleep(0.5) 

    # 1 Sekunden warten
    time.sleep(1)

# Funktion für die Live-Bewertung
def live_evaluation():    
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
            print(f"Kategorie: {CATEGORIES[category_index]} => Wahrscheinlichkeit zu niedrig ({max_probability:.4f}). Kategorie auf 'unbekannt' gesetzt.")
        else:
            print(f"Kategorie: {CATEGORIES[category_index]}")
            for i, probability in enumerate(list(output)):
                print(f"{CATEGORIES[i]}: {probability:.4f}")
                category = CATEGORIES[category_index]


        # Servo-Steuerung basierend auf der Kategorie
        steuerung(category) 
    
        # Bild im DEBUG Modus speichern
        if  DEBUG_MODE:
            save_image(image, CATEGORIES[category_index])
        
        # Warten vor der nächsten Erfassung
        time.sleep(1)

# Initialisiere ServoKit für PCA9685 mit 16 Kanälen
kit = ServoKit(channels=16)

# Konfiguration
print("Lade Konfiguration...")
TASK = 'lego'
CATEGORIES = ['leer', 'weiss', 'blau', 'gelb']
TRANSFORMS = transforms.Compose([
    transforms.ColorJitter(0.2, 0.2, 0.2, 0.2),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Kamera initialisieren
camera = USBCamera(width=224, height=224, capture_device=0)
camera.running = True
print("Die Kamera konnte erfolgreich initialisiert werden...")

# Modell initialisieren
print("Modell initialisieren...")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')  # CUDA-Gerät verwenden, wenn verfügbar
model = torchvision.models.resnet18(pretrained=True)
model.fc = torch.nn.Linear(512, len(CATEGORIES))  # Anzahl der Ausgabeklassen anpassen
model = model.to(device)

# Modell laden, falls verfügbar
model_path = '/home/winheim/nvdli-data/classification/my_model.pth'
try:
    model.load_state_dict(torch.load(model_path))
    print("Das Klassifikation Modell wurde erfolgreich geladen...")
except FileNotFoundError:
    print("Es wurde kein Klassifikation Modell gefunden. Es wird ein neues Modell verwendet....")

model.eval()  # Setze das Modell in den Evaluationsmodus
print("Chromasort ist bereit!")

# Hauptfunktion
def main():
    if DEBUG_MODE:
        print("Debug-Modus aktiviert: Bilder werden gespeichert.")
    else:
        print("Debug-Modus deaktiviert: Bilder werden nicht gespeichert.")
    
    draw_lego_brick()    
    live_evaluation()

if __name__ == "__main__":
    main()