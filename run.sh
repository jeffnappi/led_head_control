#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIR
cd $DIR
while [ 0 ];
do
  ./ola-remote.py > /dev/null 2>/dev/null
  sleep 5
  sudo /etc/init.d/olad restart
done
