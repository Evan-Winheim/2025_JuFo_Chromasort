#include <Adafruit_GFX.h>       // Bibliothek für Grafikfunktionen
#include <Adafruit_NeoMatrix.h> // Bibliothek für LED-Matrix-Steuerung
#include <Adafruit_NeoPixel.h>  // Bibliothek für NeoPixel-LEDs

// Definiere Pins für die Motorsteuerung
#define MOTOR_IN_PIN5 5  // Direktsteuerung des ersten Motors
#define MOTOR_IN_PIN3 3  // Direktsteuerung des zweiten Motors

// Definiere den Pin für die LED-Matrix
#define MATRIX_PIN 6  // WS2812B LED Data-Pin

// Konfiguration für eine 32x8 LED-Matrix
Adafruit_NeoMatrix matrix = Adafruit_NeoMatrix(32, 8, MATRIX_PIN,
  NEO_MATRIX_BOTTOM + NEO_MATRIX_RIGHT + // Startpunkt: Unten rechts
  NEO_MATRIX_COLUMNS + NEO_MATRIX_ZIGZAG, // Spaltenweise, Zick-Zack-Modus
  NEO_GRB + NEO_KHZ800); // Farbformat und Frequenz

// Farben definieren (RGB-Werte)
uint16_t blue = matrix.Color(0, 0, 255);
uint16_t white = matrix.Color(255, 255, 255);
uint16_t yellow = matrix.Color(255, 255, 0);
uint16_t colorRows[5];  // Array für verschiedene Farben im bunten Block

// Steuerung für das Blinken von Blöcken
int blinkBlock = -1;  // -1 bedeutet: Kein Block blinkt
bool showedText = false;  // Speichert, ob "CHROMASORT" bereits gezeigt wurde

void setup() {
    Serial.begin(115200); // Serielle Kommunikation für Debugging
    matrix.begin();       // Initialisiere die LED-Matrix
    matrix.setTextWrap(false);
    matrix.setBrightness(20); // Setzt die Helligkeit auf 40% 

    // Initialisiere Farben für den bunten Block (verschiedene Farben je Zeile)
    colorRows[0] = matrix.Color(0, 255, 0);       // Grün
    colorRows[1] = matrix.Color(128, 0, 128);     // Lila
    colorRows[2] = matrix.Color(255, 0, 0);       // Rot
    colorRows[3] = matrix.Color(255, 105, 180);   // Rosa
    colorRows[4] = matrix.Color(139, 69, 19);     // Braun

    // Zeige "CHROMASORT" nur einmal beim Start
    if (!showedText) {
        scrollTextRainbow("CHROMASORT");
        showedText = true;
    }

    // Zeige alle LEGO-Blöcke auf der Matrix
    drawLegoBlocks();

    // Blinken alle Blöcke einmal nacheinander    
    initBlink();

    
    // Initialisiere die Motor-Pins
    pinMode(MOTOR_IN_PIN3, OUTPUT);
    digitalWrite(MOTOR_IN_PIN3, LOW); // Motor 1 (Block 0 & 1) beim Start aus

    pinMode(MOTOR_IN_PIN5, OUTPUT);
    digitalWrite(MOTOR_IN_PIN5, LOW); // Motor 2 (Block 2 & 3) beim Start aus
}

void loop() {
    // Überprüfe, ob ein Signal von Python über die serielle Schnittstelle kommt
    if (Serial.available() > 0) {
        int receivedBlock = Serial.parseInt();  // Lese die Blocknummer (0-3)
        Serial.flush();  // Lösche alte Eingaben, um Fehler zu vermeiden
        
        // Debug-Info: Zeigt an, welche Blocknummer empfangen wurde
        Serial.print("Empfangenes Blink-Signal für Block: ");
        Serial.println(receivedBlock);

        // **Nur blinken lassen, wenn Blocknummer im gültigen Bereich ist (0-3)**
        if (receivedBlock > 0 && receivedBlock <= 4) {
            blinkBlockFor3Seconds(receivedBlock - 1, true);
        }
    }
}

// **Lässt alle Blöcke nacheinander blinken**
void initBlink() {
    for (int i = 0; i < 4; i++) {  // Jeder Block blinkt einzeln
        blinkBlockFor3Seconds(i, false);
    }
}

// **Blinkt einen Block für 3 Sekunden**
void blinkBlockFor3Seconds(int block, bool motorActive) {
    Serial.print("Blinke Block: ");
    Serial.println(block);
    
    // **Motor aktivieren, wenn notwendig**
    if ((block == 0 || block == 1) && motorActive) {
       digitalWrite(MOTOR_IN_PIN3, HIGH);  // Motor 1 an
    }
    if ((block == 2 || block == 3) && motorActive) {
       digitalWrite(MOTOR_IN_PIN5, HIGH);  // Motor 2 an
    }
    
    unsigned long startTime = millis(); // Speichert die Startzeit
    while (millis() - startTime < 3000) {  // 3 Sekunden lang blinken
        blinkSingleBlock(block);
        delay(100);  // Schnelles Blinken alle 100ms      
    }

    // Motor nach 3 Sekunden wieder ausschalten
    if (motorActive) {       
       digitalWrite(MOTOR_IN_PIN3, LOW);
       digitalWrite(MOTOR_IN_PIN5, LOW);
    }

    // Nach dem Blinken den ursprünglichen Block wiederherstellen
    restoreBlock(block);
}

// Zeichnet alle LEGO-Blöcke auf der LED-Matrix
void drawLegoBlocks() {
    matrix.fillScreen(0);

    drawBlock(1, 1, blue);      // Block 0: Blau
    drawBlock(9, 1, white);     // Block 1: Weiß
    drawBlock(17, 1, yellow);   // Block 2: Gelb
    drawColorBlock(25, 1);      // Block 3: Bunter Block

    matrix.show();
}

// Stellt einen einzelnen Block nach dem Blinken wieder her
void restoreBlock(int block) {
    switch (block) {
        case 0: drawBlock(1, 1, blue); break;
        case 1: drawBlock(9, 1, white); break;
        case 2: drawBlock(17, 1, yellow); break;
        case 3: drawColorBlock(25, 1); break;
    }
    matrix.show();
}

// Zeichnet einen einzelnen LEGO-Block (5x5 Pixel)
void drawBlock(int x, int y, uint16_t color) {
    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++) {
            matrix.drawPixel(x + j, y + i, color);
        }
    }
}

// Zeichnet den bunten LEGO-Block mit mehreren Farben
void drawColorBlock(int x, int y) {
    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++) {
            matrix.drawPixel(x + j, y + i, colorRows[i]);
        }
    }
}

// **Lässt einen einzelnen Block blinken (wechselnd sichtbar/unsichtbar)**
void blinkSingleBlock(int block) {
    static bool visible = true;
    static unsigned long lastToggleTime = 0;

    if (millis() - lastToggleTime > 100) {  // Umschalten alle 100ms
        visible = !visible;
        lastToggleTime = millis();
    }

    // Block sichtbar oder unsichtbar machen
    if (!visible) {
        matrix.fillRect(block * 8, 1, 6, 5, 0);  // Löscht den Block
    } else {
        restoreBlock(block);
    }

    matrix.show();
}

// **Scrollenden Text mit Farbverlauf auf der LED-Matrix anzeigen**
void scrollTextRainbow(const char* text) {
    int x = matrix.width();
    int textWidth = strlen(text) * 6;
    int hue = 10000;  // Farbwert-Offset für Kontrast

    while (x > -textWidth) {
        matrix.fillScreen(0);
        matrix.setCursor(x, 0);

        for (int i = 0; i < strlen(text); i++) {
            matrix.setTextColor(matrix.ColorHSV(hue, 255, 255)); // Bunte Farbe
            matrix.print(text[i]);
            hue += 30000 / strlen(text);
        }

        matrix.show();
        delay(100);
        x--;
    }
}
