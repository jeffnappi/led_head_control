#!/usr/bin/python
import sys
import os
import time

NUM_PIXELS = 168
PIXEL_SIZE = 3
LED_POWER = 0.02
MAX_POWER = NUM_PIXELS * PIXEL_SIZE * LED_POWER
MAX_BRIGHT = NUM_PIXELS * PIXEL_SIZE * 255.0
BACKUP_FILE = "boot.out"
AMP_LIMIT = 4.0

if os.path.exists('/dev/spidev0.0'):
    SPI_DEVICE = "/dev/spidev0.0"
else:
    SPI_DEVICE = "/dev/null"


GAMMA = bytearray(256)
for i in range(256):
    GAMMA[i] = int(pow(float(i) / 255.0, 2.5) * 255.0)

root = os.path.dirname(__file__)

backup_pos = 0
backup = open(root + '/' + BACKUP_FILE, 'r')
backup_data = bytearray(backup.read())
backup_end = len(backup_data)
spidev = file(SPI_DEVICE, "wb")


def Display(data):
    spidev.flush()

    pixel_values = bytearray(NUM_PIXELS * PIXEL_SIZE)

    frame_sum = 0
    for i in xrange(0, NUM_PIXELS * PIXEL_SIZE):
        pixel_values[i] = GAMMA[data[i]]
        frame_sum += pixel_values[i]

    frame_power = (frame_sum / MAX_BRIGHT) * MAX_POWER
    if frame_power > AMP_LIMIT:
        power_multiplier = 1 - ((frame_power - AMP_LIMIT) / frame_power)
        for i in xrange(0, NUM_PIXELS * PIXEL_SIZE):
            pixel_values[i] = int(pixel_values[i] * power_multiplier)

    spidev.write(pixel_values)
    spidev.flush()

def GetBackup():
    global backup_pos, NUM_PIXELS, PIXEL_SIZE, backup_end, backup_data

    backup_pos += NUM_PIXELS * PIXEL_SIZE
    if backup_pos + NUM_PIXELS * PIXEL_SIZE >= backup_end:
        print "done"
        os._exit(1)
    return backup_data[backup_pos:backup_pos + NUM_PIXELS * PIXEL_SIZE]

if __name__ == "__main__":
    while True:
        Display(GetBackup())
        time.sleep(0.05)
