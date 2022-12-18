#/bin/sh

### Uncomment this line if you need to rebuild lab_0's docker-compose-lab_0.yml file:
#../xr-compose -f lab_0-topology.yml -o docker-compose-lab_0.yml -i ios-xr/xrd-control-plane:7.8.1

echo "macvlan edits"
# macvlan for xrd01 
sed -i 's/linux:xr-120/linux:eth0/g' docker-compose-lab_0.yml
sed -i 's/xrd01-gi0: null/macvlan0: null/g' docker-compose-lab_0.yml

# macvlan for xrd07
sed -i 's/linux:xr-180/linux:eth0/g' docker-compose-lab_0.yml
sed -i 's/xrd07-gi0: null/macvlan1: null/g' docker-compose-lab_0.yml

echo "launching topology"
docker-compose -f docker-compose-lab_0.yml up --detach

echo "sudo sysctl -p"
sudo sysctl -p