#/bin/sh

../xr-compose -f ../lab_0-topology.yml -i localhost/ios-xr:7.7.1

sed -i 's/linux:xr-100/linux:eth0/g' docker-compose.yml
sed -i 's/xrd01-host: null/macvlan0: null/g' docker-compose.yml