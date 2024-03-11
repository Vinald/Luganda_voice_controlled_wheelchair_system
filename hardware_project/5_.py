# Python Script
# https://www.electronicshub.org/raspberry-pi-l298n-interface-tutorial-control-dc-motor-l298n-raspberry-pi/

import RPi.GPIO as GPIO
from time import sleep
import smbus

# Left Motor
left_in1 = 24  # GPIO pin for left motor input 1
left_in2 = 23  # GPIO pin for left motor input 2
left_en = 25  # GPIO pin for left motor enable

# Right Motor
right_in1 = 17  # GPIO pin for right motor input 1
right_in2 = 27  # GPIO pin for right motor input 2
right_en = 22  # GPIO pin for right motor enable

# LCD I2C address
lcd_address = 0x27  # I2C address of the LCD

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(left_in1, GPIO.OUT)
GPIO.setup(left_in2, GPIO.OUT)
GPIO.setup(left_en, GPIO.OUT)
GPIO.setup(right_in1, GPIO.OUT)
GPIO.setup(right_in2, GPIO.OUT)
GPIO.setup(right_en, GPIO.OUT)

# Initialize PWM
left_motor = GPIO.PWM(left_en, 1000)  # PWM object for left motor
right_motor = GPIO.PWM(right_en, 1000)  # PWM object for right motor
left_motor.start(25)  # Start left motor PWM with duty cycle 25%
right_motor.start(25)  # Start right motor PWM with duty cycle 25%

# Initialize I2C bus
bus = smbus.SMBus(1)  # Create I2C bus object

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
    command = input("Enter command (r-run, s-stop, f-forward, b-backward, l-low, m-medium, h-high, e-exit): ")

    if command == 'r':
        print("Run")
        if mode == 'both' or mode == 'left':
            GPIO.output(left_in1, GPIO.HIGH)
            GPIO.output(left_in2, GPIO.LOW)
        if mode == 'both' or mode == 'right':
            GPIO.output(right_in1, GPIO.HIGH)
            GPIO.output(right_in2, GPIO.LOW)

    elif command == 's':
        print("Stop")
        stop_motors()

    elif command == 'f':
        print("Forward")
        if mode == 'both' or mode == 'left':
            GPIO.output(left_in1, GPIO.HIGH)
            GPIO.output(left_in2, GPIO.LOW)
        if mode == 'both' or mode == 'right':
            GPIO.output(right_in1, GPIO.HIGH)
            GPIO.output(right_in2, GPIO.LOW)

    elif command == 'b':
        print("Backward")
        if mode == 'both' or mode == 'left':
            GPIO.output(left_in1, GPIO.LOW)
            GPIO.output(left_in2, GPIO.HIGH)
        if mode == 'both' or mode == 'right':
            GPIO.output(right_in1, GPIO.LOW)
            GPIO.output(right_in2, GPIO.HIGH)

    elif command == 'l':
        print("Low speed")
        left_motor.ChangeDutyCycle(25)
        right_motor.ChangeDutyCycle(25)
        update_lcd(25, mode)

    elif command == 'm':
        print("Medium speed")
        left_motor.ChangeDutyCycle(50)
        right_motor.ChangeDutyCycle(50)
        update_lcd(50, mode)

    elif command == 'h':
        print("High speed")
        left_motor.ChangeDutyCycle(75)
        right_motor.ChangeDutyCycle(75)
        update_lcd(75, mode)

    elif command == 'e':
        print("Exiting")
        stop_motors()
        left_motor.stop()
        right_motor.stop()
        GPIO.cleanup()
        break

    elif command == 'left':
        mode = 'left'
        print("Control left motor")

    elif command == 'right':
        mode = 'right'
        print("Control right motor")

    elif command == 'both':
        mode = 'both'
        print("Control both motors")

    else:
        print("Invalid command")
