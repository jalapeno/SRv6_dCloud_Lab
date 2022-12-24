#/bin/bash

echo "list docker networks"
docker network ls

echo "mapping docker networks to bridge instance files"

docker network ls | awk -F': ' '/xrd01-gi1-xrd02-gi0 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > xrd01-xrd02.txt
rm net.txt

docker network ls | awk -F': ' '/xrd01-gi2-xrd05-gi0 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > xrd01-xrd05.txt
rm net.txt

docker network ls | awk -F': ' '/xrd02-gi1-xrd03-gi0 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > xrd02-xrd03.txt
rm net.txt

docker network ls | awk -F': ' '/xrd02-gi2-xrd06-gi1 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > xrd02-xrd06.txt
rm net.txt

docker network ls | awk -F': ' '/xrd03-gi1-xrd04-gi0 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > xrd03-xrd04.txt
rm net.txt

docker network ls | awk -F': ' '/xrd04-gi1-xrd07-gi1 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > xrd04-xrd07.txt
rm net.txt

docker network ls | awk -F': ' '/xrd04-gi2-xrd05-gi1 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > xrd02-xrd05.txt
rm net.txt

docker network ls | awk -F': ' '/xrd05-gi2-xrd06-gi2 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > xrd05-xrd06.txt
rm net.txt

docker network ls | awk -F': ' '/xrd06-gi0-xrd07-gi2 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > xrd06-xrd07.txt
rm net.txt

#sudo tcpdump -ni br-"$netinstance"