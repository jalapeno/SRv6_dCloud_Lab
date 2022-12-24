#/bin/bash

docker network ls | awk -F': ' '/xrd01-gi1-xrd02-gi0 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > net0102.txt
rm net.txt

docker network ls | awk -F': ' '/xrd01-gi2-xrd05-gi0 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > net0105.txt
rm net.txt

docker network ls | awk -F': ' '/xrd02-gi1-xrd03-gi0 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > net0203.txt
rm net.txt

docker network ls | awk -F': ' '/xrd02-gi2-xrd06-gi1 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > net0206.txt
rm net.txt

docker network ls | awk -F': ' '/xrd03-gi1-xrd04-gi0 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > net0304.txt
rm net.txt

docker network ls | awk -F': ' '/xrd04-gi1-xrd07-gi1 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > net0407.txt
rm net.txt

docker network ls | awk -F': ' '/xrd04-gi2-xrd05-gi1 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > net0205.txt
rm net.txt

docker network ls | awk -F': ' '/xrd05-gi2-xrd06-gi2 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > net0506.txt
rm net.txt

docker network ls | awk -F': ' '/xrd06-gi0-xrd07-gi2 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > net0607.txt
rm net.txt

#sudo tcpdump -ni br-"$netinstance"