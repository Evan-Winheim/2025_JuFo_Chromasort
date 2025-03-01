# JUFO Projekt - CHROMASORT - Farbbasiertes Sortieren von LEGO- Steinen mit KI

Dieses Projekt wurde im Rahmen des Wettbewerbs **Jugend Forscht** von **Evan Winheim** entwickelt. Das System basiert auf einer Kombination aus **KI** und **Hardwaresteuerung**, wobei ein **Jetson Nano** für die KI-Berechnungen und ein **Arduino** für die Steuerung von LEDs und Vibrationsmotoren verwendet wird. Die KI Bilderkennung erfolgt dabei über eine am Jetson Nanon angeschlossene USB Kamera.

## Inhalt
- `app.py` – Die Hauptanwendung auf dem Jetson Nano für die Farberkennung  
- `arduino_steuerung.ino` – Die Steuerlogik für den Arduino  

---

## 1. app.py (Jetson Nano – KI-gestützte Farberkennung)
Die Datei `app.py` steuert die Farberkennung und kommuniziert mit dem Arduino.

### Funktionen:
✅ **Live-Bildverarbeitung:** Erkennt Farben aus einem Kamerastream  
✅ **KI-gestützte Klassifikation:** Nutzt neuronale Netze zur Farbzuordnung  
✅ **Serielle Kommunikation mit dem Arduino:** Sendet erkannte Farben als Zahlen (1-4)       
   - **1 = Blau**  
   - **2 = Weiss**  
   - **3 = Gelb**  
   - **4 = Unbekannt**  
   

✅ **Web-Interface:** Stellt das Video und die erkannten Farben auf einer Webseite dar  

---

## 2. arduino_steuerung.ino (Arduino – Steuerung von LEDs & Vibrationsmotoren)
Der Arduino empfängt Farbcodes vom Jetson Nano und steuert die **LED-Matrix** sowie die **Vibrationsmotoren** entsprechend.

### Funktionen:
✅ **Empfängt Befehle über den seriellen Port** (Zahl zwischen 1-4)  
   - **1 = Blau**  
   - **2 = Weiss**  
   - **3 = Gelb**  
   - **4 = Unbekannt**  

✅ **Lässt den entsprechenden LED-Block blinken** ( für 3 Sekunden)  
✅ **Aktiviert die Vibrationsmotoren während des Blinkens**  
✅ **Nutzt die Adafruit NeoPixel & NeoMatrix Bibliotheken für die LED-Steuerung**  

---

## Lizenz
Dieses Projekt steht unter der MIT-Lizenz. Siehe die LICENSE-Datei für Details.

## Weiterführende Informationen
Weitere Details und die vollständige Implementierung finden Sie in den einzelnen Quellcodedateien des Projekts.