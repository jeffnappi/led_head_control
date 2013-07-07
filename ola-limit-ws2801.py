#!/usr/bin/python
import sys
import time
import random
import argparse
from ola.ClientWrapper import ClientWrapper

NUM_PIXELS = 168
PIXEL_SIZE = 3
LED_POWER = 0.02
MAX_POWER = NUM_PIXELS * PIXEL_SIZE * LED_POWER
MAX_BRIGHT = NUM_PIXELS * PIXEL_SIZE * 255.0
SPI_DEVICE = "/dev/spidev0.0";
BACKUP_FILE = "save.out"
AMP_LIMIT = 4.0

GAMMA = bytearray(256)
for i in range(256): GAMMA[i] = int(pow(float(i) / 255.0, 2.5) * 255.0)

zero_count = 0

def Display(data):
  spidev.flush()
  pixel_values = bytearray(NUM_PIXELS * PIXEL_SIZE)

  frame_sum = 0
  for i in xrange(0,NUM_PIXELS * PIXEL_SIZE):
    pixel_values[i] = GAMMA[data[i]]
    frame_sum += pixel_values[i]

  frame_power = (frame_sum / MAX_BRIGHT) * MAX_POWER
  if frame_power > AMP_LIMIT:
    power_multiplier = 1-((frame_power - AMP_LIMIT) / frame_power)
    for i in xrange(0,NUM_PIXELS * PIXEL_SIZE):
      pixel_values[i] = int(pixel_values[i] * power_multiplier)

  spidev.write(pixel_values)
  spidev.flush()

def Receive(data):
  global zero_count, time_last

  if backup_mode:
    if sum(data) == 0:
      print "Done saving."
      quit()
    backup.write(data[:NUM_PIXELS * PIXEL_SIZE])

  if sum(data) != 0:
    time_last = time.time()
    Display(data)

def GetBackup():
  global backup_pos
  backup_pos += NUM_PIXELS * PIXEL_SIZE
  if backup_pos + NUM_PIXELS * PIXEL_SIZE >= backup_end: backup_pos = 0
  return backup_data[backup_pos:backup_pos + NUM_PIXELS * PIXEL_SIZE]

# check to see if we are receiving data. if not play backup
def CheckAlive():
  global time_last, wrapper
  if time.time() - time_last > 5:
    Display(GetBackup())
    wrapper.AddEvent(20, CheckAlive)
  else:
    wrapper.AddEvent(1000, CheckAlive)


backup_mode = True if len(sys.argv) > 1 and sys.argv[1] == "-b" else False

time_last = time.time()

if backup_mode:
  backup = open(BACKUP_FILE,'wb')
  backup_data = bytearray()
else:
  backup = open(BACKUP_FILE,'r')
  backup_data = bytearray(backup.read())

backup_pos = 0
backup_end = len(backup_data)

spidev = file(SPI_DEVICE, "wb")
universe = 1
wrapper = ClientWrapper()
client = wrapper.Client()
client.RegisterUniverse(universe, client.REGISTER, Receive)
if not backup_mode: wrapper.AddEvent(1000, CheckAlive)
wrapper.Run()
