from adafruit_servokit import ServoKit
import time
import serial
_step_size = 1

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1, dsrdtr=True, rtscts=True)
time.sleep(2)

# Initialisiere ServoKit für PCA9685 mit 16 Kanälen
kit = ServoKit(channels=16)

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

def blink_block(block_number):
    """Sendet die Blocknummer (0-3) zum Blinken an den Arduino."""
    message = f"{block_number}\n"
    ser.write(message.encode('utf-8'))
    print(f"Block {block_number} blinkt für 3 Sekunden.")


try:

    print("servo_test wird ausgeführt")
    # Teste die Servos
    
    # Hinten
    print("hinten")    
    move_servo_slowly(channel=0, start_angle=90, end_angle=45, step_size=_step_size, delay=0.05)    
    time.sleep(0.5)    
    move_servo_slowly(channel=0, start_angle=45, end_angle=90, step_size=_step_size, delay=0.05)
    blink_block(1)  # Blauer Block blinkt
    time.sleep(0.5)
    

    # Links   
    print("links") 
    move_servo_slowly(channel=15, start_angle=90, end_angle=45, step_size=_step_size, delay=0.05)    
    time.sleep(0.5)    
    move_servo_slowly(channel=15, start_angle=45, end_angle=90, step_size=_step_size, delay=0.05)
    blink_block(2)  # Weißer Block blinkt
    time.sleep(0.5)

    # rechts
    print("rechts")
    move_servo_slowly(channel=15, start_angle=90, end_angle=135, step_size=_step_size, delay=0.05)
    time.sleep(0.5)
    move_servo_slowly(channel=15, start_angle=135, end_angle=90, step_size=_step_size, delay=0.05)
    blink_block(3)  # Gelber Block blinkt
    time.sleep(0.5)

    # vorne
    print("vorne") 
    move_servo_slowly(channel=0, start_angle=90, end_angle=135, step_size=_step_size, delay=0.05)    
    time.sleep(0.5)    
    move_servo_slowly(channel=0, start_angle=135, end_angle=90, step_size=_step_size, delay=0.05)
    blink_block(4)  # Bunter Block blinkt
    time.sleep(0.5)
    
    # mitte
    print("mitte")
    move_servo_slowly(channel=15, start_angle=90, end_angle=90, step_size=_step_size, delay=0.05)
    time.sleep(0.5)
    move_servo_slowly(channel=0, start_angle=90, end_angle=90, step_size=_step_size, delay=0.05)

    print("Programm beendet.")
    	

except KeyboardInterrupt:
    print("Programm beendet.")
