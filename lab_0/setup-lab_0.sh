#/bin/sh

../xr-compose -f lab_0-topology.yml -o docker-compose-lab_0.yml -i ios-xr/xrd-control-plane:7.8.1

# macvlan for xrd01 
sed -i 's/linux:xr-120/linux:eth0/g' docker-compose-lab_0.yml
sed -i 's/xrd01-gi0: null/macvlan0: null/g' docker-compose-lab_0.yml

# macvlan for xrd07
sed -i 's/linux:xr-180/linux:eth1/g' docker-compose-lab_0.yml
sed -i 's/xrd07-gi0: null/macvlan1: null/g' docker-compose-lab_0.yml

docker-compose -f docker-compose-lab_0.yml up --detach
