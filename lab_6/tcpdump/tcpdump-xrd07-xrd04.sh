#/bin/bash

docker network ls | awk -F': ' '/xrd04-gi1-xrd07-gi1 /{print $0}' > dockernets.txt
netinstance=$( head -n 1 dockernets.txt | cut -c 1-12 )
sudo tcpdump -ni br-"$netinstance"