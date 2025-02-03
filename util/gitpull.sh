#!/bin/bash

export HOME=/home/cisco
cd /home/cisco/SRv6_dCloud_Lab
git config --global --add safe.directory /home/cisco/SRv6_dCloud_Lab
git fetch origin
git reset --hard origin/main 

cd /home/cisco/srctl
git config --global --add safe.directory /home/cisco/srctl
git fetch origin
git reset --hard origin/main 

cd /home/cisco
chown cisco:cisco -R /home/cisco/SRv6_dCloud_Lab
chown cisco:cisco -R /home/cisco/srctl
