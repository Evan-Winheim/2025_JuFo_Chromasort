# sudo LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1 python3.6 test_bilder.py

# -*- coding: utf-8 -*-
import torch
import torchvision.transforms as transforms
import torch.nn.functional as F
import torchvision.models as models
import cv2
import numpy as np
import os
from utils import preprocess

# Matplotlib "headless" setzen (muss VOR pyplot importiert werden)
import matplotlib
matplotlib.use('Agg')  # "Headless"-Modus aktivieren (keine GUI nötig)
import matplotlib.pyplot as plt  # Jetzt pyplot importieren



# Verzeichnis mit Testbildern
test_images_dir = os.path.expanduser("~/nvdli-data/classification/lego_A/blau/")

# Kategorien, die das Modell kennt
CATEGORIES = ['leer', 'weiss', 'blau', 'gelb']

# Modell auf Evaluation setzen
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ResNet-18 Modell laden
model = models.resnet18(pretrained=True)
model.fc = torch.nn.Linear(512, 4)  # Anzahl der Klassen (leer, weiß, blau, gelb)

# Modell auf GPU oder CPU setzen
model = model.to(device)

# Modellgewichte laden (falls du bereits ein trainiertes Modell hast)
model_path = "/home/winheim/nvdli-data/classification/my_model.pth"
try:
    model.load_state_dict(torch.load(model_path, map_location=device))
    print("Modell erfolgreich geladen!")
except FileNotFoundError:
    print("WARNUNG: Kein trainiertes Modell gefunden, es wird ein zufälliges Modell verwendet.")

# Modell auf Evaluationsmodus setzen
model.eval()

# Farbbereiche für Visualisierung in HSV
def show_hsv_histogram(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])  # Hue
    hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])  # Saturation
    hist_v = cv2.calcHist([hsv], [2], None, [256], [0, 256])  # Value

    plt.figure(figsize=(12, 4))

    plt.subplot(1, 3, 1)
    plt.title("Hue (Farbton)")
    plt.plot(hist_h, color="r")

    plt.subplot(1, 3, 2)
    plt.title("Saturation (Sättigung)")
    plt.plot(hist_s, color="g")

    plt.subplot(1, 3, 3)
    plt.title("Value (Helligkeit)")
    plt.plot(hist_v, color="b")

    plt.show()

# Testbilder durchgehen
for img_name in os.listdir(test_images_dir):
    img_path = os.path.join(test_images_dir, img_name)
    
    # Bild laden
    image = cv2.imread(img_path)
    if image is None:
        print(f"Fehler beim Laden von {img_name}, überspringe...")
        continue

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # In RGB konvertieren

    # HSV Histogramm anzeigen
    show_hsv_histogram(image)

    # Bild vorverarbeiten
    preprocessed = preprocess(image).to(device)

    # Modellvorhersage berechnen
    output = model(preprocessed)
    probabilities = F.softmax(output, dim=1).detach().cpu().numpy().flatten()

    # Ergebnisse ausgeben
    print(f"\n*** Teste Bild: {img_name} ***")
    for i, prob in enumerate(probabilities):
        print(f"{CATEGORIES[i]}: {prob:.2f}")

    # Höchste Wahrscheinlichkeit als Klasse wählen
    predicted_category = CATEGORIES[probabilities.argmax()]
    max_prob = probabilities.max()

    print(f"\nErkannte Kategorie: {predicted_category} mit {max_prob:.2f} Wahrscheinlichkeit")
    print("-" * 50)
