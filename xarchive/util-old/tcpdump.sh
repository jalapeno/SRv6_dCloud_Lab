#!/bin/bash

line=$(head -n 1 $1)
echo "sudo tcpdump -lni $line"
sudo tcpdump -lni $line
