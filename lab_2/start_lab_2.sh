#/bin/sh

# macvlan for xrd01 
#sed -i 's/linux:xr-120/linux:eth0/g' docker-compose.yml
#sed -i 's/xrd01-gi0: null/macvlan0: null/g' docker-compose.yml

# macvlan for xrd07
#sed -i 's/linux:xr-180/linux:eth0/g' docker-compose.yml
#sed -i 's/xrd07-gi0: null/macvlan0: null/g' docker-compose.yml

docker-compose -f docker-compose.yml up --detach