#/bin/bash

docker network ls | awk -F': ' '/xrd04-gi2-xrd05-gi1 /{print $0}' > net0405.txt
netinstance=$( head -n 1 net0405.txt | cut -c 1-12 )
sudo tcpdump -ni br-"$netinstance"