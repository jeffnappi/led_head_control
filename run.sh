#!/bin/bash
cd /home/pi/ola_limit_ws2801
while [ 0 ];
do
  ./ola-limit-ws2801.py > /dev/null 2>/dev/null
  sleep 5
  sudo /etc/init.d/olad restart
done
