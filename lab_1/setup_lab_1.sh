#/bin/sh

../xr-compose -f lab_1-topology.yml -i localhost/ios-xr:7.7.1

# macvlan for xrd01 
sed -i 's/linux:xr-120/linux:eth0/g' docker-compose.yml
sed -i 's/xrd01-gi0: null/macvlan0: null/g' docker-compose.yml

# macvlan for xrd07
sed -i 's/linux:xr-180/linux:eth1/g' docker-compose.yml
sed -i 's/xrd07-gi0: null/macvlan1: null/g' docker-compose.yml

#docker-compose -f docker-compose.yml up --detach
