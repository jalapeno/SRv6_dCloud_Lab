#/bin/bash

echo "list docker networks"
docker network ls

echo "mapping docker networks to bridge instance files"

docker network ls | awk -F': ' '/xrd01-gi1-xrd02-gi0 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > /home/cisco/SRv6_dCloud_Lab/util/xrd01-xrd02
echo br-"$netinstance"

brctl show | grep br-"$netinstance" > br.txt 
veth=$(rev br.txt | cut -c -11 | rev ) > veth.txt
sudo tc qdisc add dev $veth root netem delay 10000

#rm net.txt
#rm br.txt
rm veth.txt

docker network ls | awk -F': ' '/xrd01-gi2-xrd05-gi0 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > /home/cisco/SRv6_dCloud_Lab/util/xrd01-xrd05
echo br-"$netinstance"
rm net.txt

docker network ls | awk -F': ' '/xrd02-gi1-xrd03-gi0 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > /home/cisco/SRv6_dCloud_Lab/util/xrd02-xrd03
echo br-"$netinstance"
rm net.txt

docker network ls | awk -F': ' '/xrd02-gi2-xrd06-gi1 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > /home/cisco/SRv6_dCloud_Lab/util/xrd02-xrd06
echo br-"$netinstance"
rm net.txt

docker network ls | awk -F': ' '/xrd03-gi1-xrd04-gi0 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > /home/cisco/SRv6_dCloud_Lab/util/xrd03-xrd04
echo br-"$netinstance"
rm net.txt

docker network ls | awk -F': ' '/xrd04-gi1-xrd07-gi1 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > /home/cisco/SRv6_dCloud_Lab/util/xrd04-xrd07
echo br-"$netinstance"
rm net.txt

docker network ls | awk -F': ' '/xrd04-gi2-xrd05-gi1 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > /home/cisco/SRv6_dCloud_Lab/util/xrd04-xrd05
echo br-"$netinstance"
rm net.txt

docker network ls | awk -F': ' '/xrd05-gi2-xrd06-gi2 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > /home/cisco/SRv6_dCloud_Lab/util/xrd05-xrd06
echo br-"$netinstance"
rm net.txt

docker network ls | awk -F': ' '/xrd06-gi0-xrd07-gi2 /{print $0}' > net.txt
netinstance=$( head -n 1 net.txt | cut -c 1-12 )
echo br-"$netinstance" > /home/cisco/SRv6_dCloud_Lab/util/xrd06-xrd07
echo br-"$netinstance"
rm net.txt
