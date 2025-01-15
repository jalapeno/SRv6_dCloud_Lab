#!/bin/bash

line=$(head -n 1 xrd01-xrd05)
echo "
running tcpdump on xrd01 to xrd05 link

"
echo "sudo tcpdump -ni $line"
sudo tcpdump -ni $line &
sleep 3
pid=$(ps -e | pgrep tcpdump)  
echo $pid  
sudo kill -9 $pid
echo "
stopping tcpdump
"

line=$(head -n 1 xrd04-xrd05)
echo "running tcpdump on xrd05 to xrd04 link
"
echo "sudo tcpdump -ni $line

"
sudo tcpdump -ni $line &
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
echo "sudo tcpdump -ni $line

"
sudo tcpdump -ni $line &
sleep 3
pid=$(ps -e | pgrep tcpdump)  
echo $pid  
sudo kill -9 $pid
echo "
stopping tcpdump
"
