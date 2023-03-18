#/bin/bash

line=$(head -n 1 xrd01-xrd05)
echo "sudo tcpdump -ni $line"
timeout 3s sudo tcpdump -ni $line
echo "stop tcpdump"

line=$(head -n 1 xrd05-xrd06)
echo "sudo tcpdump -ni $line"
timeout 3s sudo tcpdump -ni $line
echo "stop tcpdump"

line=$(head -n 1 xrd06-xrd07)
echo "sudo tcpdump -ni $line"
timeout 3s sudo tcpdump -ni $line
echo "stop tcpdump"