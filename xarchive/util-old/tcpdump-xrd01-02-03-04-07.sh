#!/bin/bash

line=$(head -n 1 xrd01-xrd02)
echo "
running tcpdump on xrd01 to xrd02 link

"
echo "sudo tcpdump -lni $line"
sudo tcpdump -lni $line &
sleep 3
pid=$(ps -e | pgrep tcpdump)  
echo $pid  
sudo kill -9 $pid
echo "
stopping tcpdump
"

line=$(head -n 1 xrd02-xrd03)
echo "running tcpdump on xrd02 to xrd03 link
"
echo "sudo tcpdump -lni $line

"
sudo tcpdump -lni $line &
sleep 3
pid=$(ps -e | pgrep tcpdump)  
echo $pid  
sudo kill -9 $pid
echo "
stopping tcpdump
"
echo "running tcpdump on xrd03 to xrd04 link

"
line=$(head -n 1 xrd03-xrd04)
echo "sudo tcpdump -lni $line

"
sudo tcpdump -lni $line &
sleep 3
pid=$(ps -e | pgrep tcpdump)  
echo $pid  
sudo kill -9 $pid
echo "
stopping tcpdump
"
echo "running tcpdump on xrd04 to xrd07 link

"
line=$(head -n 1 xrd04-xrd07)
echo "sudo tcpdump -lni $line

"
sudo tcpdump -lni $line &
sleep 3
pid=$(ps -e | pgrep tcpdump)  
echo $pid  
sudo kill -9 $pid
echo "
stopping tcpdump
"