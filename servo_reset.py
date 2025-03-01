from adafruit_servokit import ServoKit
import time

_step_size = 1

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

try:
    
    # mitte
    print("mitte")
    move_servo_slowly(channel=15, start_angle=90, end_angle=90, step_size=_step_size, delay=0.05)
    time.sleep(0.5)
    move_servo_slowly(channel=0, start_angle=90, end_angle=90, step_size=_step_size, delay=0.05)

    print("Programm beendet.")
    	

except KeyboardInterrupt:
    print("Programm beendet.")
