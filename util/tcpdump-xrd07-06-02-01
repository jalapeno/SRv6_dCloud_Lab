#/bin/bash

line=$(head -n 1 xrd06-xrd07)
echo "
running tcpdump on xrd06 to xrd07 link

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

line=$(head -n 1 xrd02-xrd06)
echo "running tcpdump on xrd02 to xrd06 link
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
echo "running tcpdump on xrd01 to xrd02 link

"
line=$(head -n 1 xrd01-xrd02)
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
