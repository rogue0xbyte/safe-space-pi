import random
import serial
import RPi.GPIO as GPIO
import time
from datetime import datetime
import os, json

MQ2_DO_PIN =  13
MQ9_DO_PIN =  13
R0 = 0.91

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1, dsrdtr=False, xonxoff=0, rtscts=True)
# ser.reset_input_buffer()

recieveInput = False
session_no = 0

JOB = ""
EQPT = ""

def read_job_equipment_from_file():
    global JOB, EQPT
    try:
        last_eqfile = 0
        for i in os.listdir():
            if i.startswith("job_equipment-"):
                eqfile_no = int(i.split("job_equipment-")[-1].split(".json")[0])
                if last_eqfile<eqfile_no:
                    last_eqfile = eqfile_no
        with open(f"job_equipment-{last_eqfile}.json", "r") as f:
            data = json.load(f)
            JOB = data.get("JOB", "")[:8]
            EQPT = data.get("EQPT", "")[:8]
            print(JOB, EQPT)
        for i in range(last_eqfile):
            try:
                os.remove(f"job_equipment-{i}.json")
            except:
                pass
    except FileNotFoundError:
        with open("job_equipment-0.json", "w") as f:
            json.dump({"JOB": JOB, "EQPT": EQPT}, f)
        pass
    except Exception as e:
        print("Failed to read job name and equipment number from file:", e)

read_job_equipment_from_file()

ALERT = 0

start_time = datetime.now()

with open("data/session-history.csv", "w") as f:
    f.write("ID, CO, LEL, H2S, JOB, EQPT, TIME_IN, TIME_OUT\n")

def calculate_elapsed_time(start_time):
    # Calculate the elapsed time
    elapsed_time = datetime.now() - start_time

    # Convert elapsed time to seconds
    total_seconds = int(elapsed_time.total_seconds())

    # Calculate hours, minutes, and seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Format the elapsed time as HH:MM:SS
    elapsed_time_str = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

    return elapsed_time_str

def get_current_time():
    # Get the current local time
    current_time = datetime.now().strftime("%H:%M:%S")
    return current_time

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(MQ2_DO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(MQ9_DO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def MQ(id:int):
    if id==9:
        DO_PIN = MQ9_DO_PIN
    else:
        DO_PIN = MQ2_DO_PIN
    try:
        alarm = 0
        sensor_volt = 0.0
        RS_gas = 0.0
        ratio = 0.0

        sensorValue = analog_read(DO_PIN)
        sensor_volt = (sensorValue / 1024.0) * 5.0
        RS_gas = (5.0 - sensor_volt) / sensor_volt

        ratio = abs(RS_gas / 2*R0)
        if MQ2_DO_PIN == MQ9_DO_PIN:
            if id==2:
                return (ratio*0.42)
            if id==3:
                return (ratio/200)

        if id==2:
            return (ratio*100)
        if id==3:
            return (ratio/2)

        return ratio
    except Exception as e:
        print(e)
        return None

def analog_read(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.1)

    GPIO.setup(pin, GPIO.IN)

    count = 0
    while GPIO.input(pin) == GPIO.LOW:
        count += 1

    return count

def loop():
    global recieveInput, session_no, start_time, ALERT
    print("started.")
    while True:
        try:
            if recieveInput:
                CO = round(MQ(9), 2)
                LEL = round(MQ(3), 2)
                H2S = round(MQ(2), 2)

                # Thresholds
                # print("MQ9: CO",CO)
                # print("MQ2: H2S",H2S)
                # print("MQ2: LEL",LEL)
                if CO>400:
                    ALERT=1
                elif H2S>500:
                    ALERT=1
                elif LEL>10:
                    ALERT=1
                else:
                    ALERT=0


                # Concatenate the values with a delimiter and encode them
                message = f"{calculate_elapsed_time(start_time)}|{CO}|{LEL}|{H2S}|{JOB}|{get_current_time()}"
                if ALERT==1:
                    message += "|SOS"

                message += "\n"
                message = message.encode('utf-8')
                # Write the message to the serial port
                # print(message)
                ser.write(message)

            # Wait to receive acknowledgment from the Arduino
            acknowledgment = ser.readline().decode('utf-8').strip()

            if acknowledgment == "ACK":
                if recieveInput==False:
                    session_no += 1
                    start_time = datetime.now()
                    read_job_equipment_from_file()
                    with open(f"data/session-{session_no}.csv", "w") as f:
                        f.write("CO, LEL, H2S\n")
                else:
                    with open(f"data/session-{session_no}.csv", "a") as f:
                        f.write(f"{CO:2f}, {LEL:2f}, {H2S:2f}\n")

                recieveInput = True
            else:
                if recieveInput==True:
                    with open("data/session-history.csv", "a") as f:
                        with open(f"data/session-{session_no}.csv", "r") as sf:
                            CO, LEL, H2S = 0, 0, 0
                            slines = sf.readlines()
                            for row in slines:
                                try:
                                    CO += float(row.split(", ")[0].strip().replace("\n",""))
                                    LEL += float(row.split(", ")[1].strip().replace("\n",""))
                                    H2S += float(row.split(", ")[2].strip().replace("\n",""))
                                except:
                                    continue
                        CO, LEL, H2S = CO/len(slines), LEL/len(slines), H2S/len(slines)
                        TIME_IN = start_time.strftime("%H:%M:%S")
                        TIME_OUT = get_current_time()
                        f.write(f"{session_no}, {CO:2f}, {LEL:2f}, {H2S:2f}, {JOB}, {EQPT}, {TIME_IN}, {TIME_OUT}\n")
                recieveInput = False
        except:
            continue

if __name__ == '__main__':
    try:
        setup()
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
