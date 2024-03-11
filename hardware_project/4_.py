import RPi.GPIO as GPIO
from time import sleep
import smbus

# Left Motor
left_in1 = 24
left_in2 = 23
left_en = 25

# Right Motor
right_in1 = 17
right_in2 = 27
right_en = 22

# LCD I2C address
lcd_address = 0x27

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(left_in1, GPIO.OUT)
GPIO.setup(left_in2, GPIO.OUT)
GPIO.setup(left_en, GPIO.OUT)
GPIO.setup(right_in1, GPIO.OUT)
GPIO.setup(right_in2, GPIO.OUT)
GPIO.setup(right_en, GPIO.OUT)

# Initialize PWM
left_motor = GPIO.PWM(left_en, 1000)
right_motor = GPIO.PWM(right_en, 1000)
left_motor.start(25)
right_motor.start(25)

# Initialize I2C bus
bus = smbus.SMBus(1)

# Function to stop motors
def stop_motors():
    GPIO.output(left_in1, GPIO.LOW)
    GPIO.output(left_in2, GPIO.LOW)
    GPIO.output(right_in1, GPIO.LOW)
    GPIO.output(right_in2, GPIO.LOW)

# Function to update LCD
def update_lcd(speed, mode):
    bus.write_byte(lcd_address, 0xFE)  # Command prefix for LCD control
    bus.write_byte(lcd_address, 0x01)  # Clear display command
    bus.write_byte(lcd_address, ord("M"))
    bus.write_byte(lcd_address, ord("o"))
    bus.write_byte(lcd_address, ord("t"))
    bus.write_byte(lcd_address, ord("o"))
    bus.write_byte(lcd_address, ord("r"))
    bus.write_byte(lcd_address, ord(" "))
    bus.write_byte(lcd_address, ord("S"))
    bus.write_byte(lcd_address, ord("p"))
    bus.write_byte(lcd_address, ord("e"))
    bus.write_byte(lcd_address, ord("e"))
    bus.write_byte(lcd_address, ord("d"))
    bus.write_byte(lcd_address, ord(":"))
    bus.write_byte(lcd_address, ord(" "))
    bus.write_byte(lcd_address, ord(str(speed)))
    bus.write_byte(lcd_address, ord("%"))
    bus.write_byte(lcd_address, 0xC0)  # Move cursor to the second line
    bus.write_byte(lcd_address, ord("Mode: " + mode))

# User interaction loop
mode = 'both'  # Initial mode
while True:
    command = input("Enter command (l-left, r-right, lr-both, s-stop, l-low, m-medium, h-high, e-exit): ")

    if command == 'l':
        print("Control left motor")
        mode = 'left'

    elif command == 'r':
        print("Control right motor")
        mode = 'right'

    elif command == 'lr':
        print("Control both motors")
        mode = 'both'

    elif command == 's':
        print("Stop")
        stop_motors()

    elif command == 'l' or command == 'm' or command == 'h':
        speed = 25 if command == 'l' else (50 if command == 'm' else 75)
        print(f"Set speed to {speed}")
        left_motor.ChangeDutyCycle(speed)
        right_motor.ChangeDutyCycle(speed)
        update_lcd(speed, mode)

    elif command == 'e':
        print("Exiting")
        stop_motors()
        left_motor.stop()
        right_motor.stop()
        GPIO.cleanup()
        break

    else:
        print("Invalid command")
