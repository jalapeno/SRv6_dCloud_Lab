#/bin/sh

# this script was developed to setup Cisco Live SRv6 Lab environment
# it launches an XRd topology and a pair of Ubuntu VMs which it then 
# attaches to the topology 

echo "starting setup: " >> /home/cisco/startup.log

#./xr-compose -f docker-compose-6-node.yml  -li localhost/ios-xr:7.8.1.18I
#sudo sysctl -p
#echo "sleeping for 10 seconds to let images build" >> /home/cisco/startup.log
#sleep 10

docker network ls | awk -F': ' '/srv6_dcloud_lab_mgmt /{print $0}' > /home/cisco/mgt_br.txt
mgt_br=$( head -n 1 mgt_br.txt | cut -c 1-12 )

echo "$mgt_br"
ifconfig br-"$mgt_br"



