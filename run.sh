#!/bin/bash

cd /home/pi/led_head_control

echo "running from $DIR"
while [ 0 ];
do
  ./ola-remote.py > /dev/null 2>/dev/null
  sleep 5
  sudo /etc/init.d/olad restart
done
