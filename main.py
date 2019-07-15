import serial
import time
import random
import subprocess


def baudCheck():
    successful_transmissions = 0
    for j in range(0, 10):
        packet = bytearray()
        for i in range(0, 16):
            packet.append(0xCC)

        packet.append(0x55)
        for i in range(0x40, 0x50):
            packet.append(i)

        ser1.write(packet)
        ser1.flush()

        s = ser2.read(16)
        if s == b'@ABCDEFGHIJKLMNO':
            successful_transmissions += 1
    return successful_transmissions


def change_baud(baud):
    ser1.baudrate = baud
    reset_mcu()
    time.sleep(2)
    ser2.reset_input_buffer()


def reset_mcu():
    subprocess.run(["avrdude", "-c", "usbasp", "-p", "atmega328pb", "-B5"], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


ser1, ser2 = (serial.Serial('COM19', 100),                          # trans
              serial.Serial('COM17', baudrate=9600, timeout=0.7))   # recv
was_successful = False
unsuccessful_trials = 0

reset_mcu()
# IMPORTANT! Sleep for 1s until the Controller is ready!
time.sleep(2)

print("---[ STD BAUD ]---")

std_baud = [300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 56000, 57600, 115200, 256000]
std_baud_max = 0

for num, baud in enumerate(std_baud):
    change_baud(baud)
    successful = baudCheck()
    print("{:=5}: {:>3}".format(baud, successful))
    if successful > 0:
        std_baud_max = num

if std_baud_max < len(std_baud):
    std_baud_max = std_baud[std_baud_max + 1]
else:
    std_baud_max = std_baud[std_baud_max]

print("---[ RND BAUD (", std_baud_max, ") ]---")

for baud in range(0, std_baud_max, 1000):
    baud += random.randint(1, 100)
    change_baud(baud)
    successful = baudCheck()
    if successful < 10 and was_successful and unsuccessful_trials < 10:
        for baud in range(baud - 1000, baud, 100):
            baud += random.randint(1, 100)
            ser1.baudrate = baud
            time.sleep(3)
            successful = baudCheck()
            print("{:=5}: {:>3}".format(baud, successful))
            if successful < 10:
                unsuccessful_trials += 1
    else:
        if successful > 0:
            was_successful = True
            unsuccessful_trials = 0
        print("{:=5}: {:>3}".format(baud, successful))