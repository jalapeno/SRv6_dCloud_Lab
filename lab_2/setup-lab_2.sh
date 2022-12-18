#/bin/sh

### Uncomment this line if you need to rebuild lab_1's docker-compose-lab_2.yml file:
#../xr-compose -f lab_2-topology.yml -o docker-compose-lab_2.yml -i ios-xr/xrd-control-plane:7.8.1

echo "make sure macvlan edits are in place"
# macvlan for xrd01 
sed -i 's/linux:xr-120/linux:eth0/g' docker-compose-lab_2.yml
sed -i 's/xrd01-gi0: null/macvlan0: null/g' docker-compose-lab_2.yml

# macvlan for xrd07
sed -i 's/linux:xr-180/linux:eth0/g' docker-compose-lab_2.yml
sed -i 's/xrd07-gi0: null/macvlan1: null/g' docker-compose-lab_2.yml

echo "launching topology"
docker-compose -f docker-compose-lab_2.yml up --detach

echo "sudo sysctl -p"
sudo sysctl -p
    