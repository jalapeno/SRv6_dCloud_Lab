#/bin/bash

echo "sudo tcpdump -ni xrd01-xrd05"
sudo tcpdump -ni xrd01-xrd05

sleep 3

break

echo "sudo tcpdump -ni xrd05-xrd06"
sudo tcpdump -ni xrd05-xrd06

sleep 3

break

echo "sudo tcpdump -ni xrd06-xrd07"
sudo tcpdump -ni xrd06-xrd07

sleep 3

break