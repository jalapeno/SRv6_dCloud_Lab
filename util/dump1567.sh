#/bin/bash

line=$(head -n 1 xrd01-xrd05)
echo "sudo tcpdump -ni $line"
sudo tcpdump -ni $line
sleep 4
pid=$(ps -e | pgrep tcpdump)  
echo $pid  
sudo kill -2 $pid
echo "stop tcpdump"

line=$(head -n 1 xrd05-xrd06)
echo "sudo tcpdump -ni $line"
sudo tcpdump -ni $line
sleep 4
pid=$(ps -e | pgrep tcpdump)  
echo $pid  
sudo kill -2 $pid
echo "stop tcpdump"

line=$(head -n 1 xrd06-xrd07)
echo "sudo tcpdump -ni $line"
sudo tcpdump -ni $line
sleep 4
pid=$(ps -e | pgrep tcpdump)  
echo $pid  
sudo kill -2 $pid
echo "stop tcpdump"
