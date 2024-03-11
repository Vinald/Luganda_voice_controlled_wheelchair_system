import RPi.GPIO as GPIO
from time import sleep

# Motor 1
in1 = 24
in2 = 23
en1 = 25

# Motor 2
in3 = 17
in4 = 27
en2 = 22

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(en1, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(en2, GPIO.OUT)

# Initialize PWM
p1 = GPIO.PWM(en1, 1000)
p2 = GPIO.PWM(en2, 1000)
p1.start(25)
p2.start(25)

# Function to stop motors
def stop_motors():
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)

# User interaction loop
while True:
    command = input("Enter command (r-run, s-stop, f-forward, b-backward, l-low, m-medium, h-high, e-exit): ")

    if command == 'r':
        print("Run")
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in4, GPIO.LOW)

    elif command == 's':
        print("Stop")
        stop_motors()

    elif command == 'f':
        print("Forward")
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in4, GPIO.LOW)

    elif command == 'b':
        print("Backward")
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)

    elif command == 'l':
        print("Low speed")
        p1.ChangeDutyCycle(25)
        p2.ChangeDutyCycle(25)

    elif command == 'm':
        print("Medium speed")
        p1.ChangeDutyCycle(50)
        p2.ChangeDutyCycle(50)

    elif command == 'h':
        print("High speed")
        p1.ChangeDutyCycle(75)
        p2.ChangeDutyCycle(75)

    elif command == 'e':
        print("Exiting")
        stop_motors()
        p1.stop()
        p2.stop()
        GPIO.cleanup()
        break

    else:
        print("Invalid command")
