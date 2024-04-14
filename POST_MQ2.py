import RPi.GPIO as GPIO
import time

def setup():
    global DO_PIN, R0
    DO_PIN =  16
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(DO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    R0 = 0.91

def analog_read(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.1)

    GPIO.setup(pin, GPIO.IN)

    count = 0
    while GPIO.input(pin) == GPIO.LOW:
        count += 1

    return count

def main():
    global DO_PIN, R0
    while True:
        try:
            alarm = 0
            sensor_volt = 0.0
            RS_gas = 0.0
            ratio = 0.0

            sensorValue = analog_read(DO_PIN)
            sensor_volt = (sensorValue / 1024.0) * 5.0
            RS_gas = (5.0 - sensor_volt) / sensor_volt

            ratio = abs(RS_gas / R0)
            print(ratio*100)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    setup()
    main()
