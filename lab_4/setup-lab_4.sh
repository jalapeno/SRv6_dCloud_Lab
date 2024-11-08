#!/bin/sh

### run cleanup script to eliminate any stale docker network instances or volumes 

./cleanup-lab_4.sh

### Uncomment these lines if you need to rebuild lab_4's docker-compose-lab_4.yml file:

# ../xr-compose -f lab_4-topology.yml -o docker-compose-lab_4.yml -i ios-xr/xrd-control-plane:7.8.1

# sed -i 's/linux:xr-120/linux:eth0/g' docker-compose-lab_4.yml
# sed -i 's/xrd01-gi0: null/macvlan0: null/g' docker-compose-lab_4.yml

# sed -i 's/linux:xr-130/linux:eth1/g' docker-compose-lab_4.yml
# sed -i 's/xrd01-gi3: null/macvlan3: null/g' docker-compose-lab_4.yml

# sed -i 's/linux:xr-180/linux:eth0/g' docker-compose-lab_4.yml
# sed -i 's/xrd07-gi0: null/macvlan1: null/g' docker-compose-lab_4.yml

# sed -i 's/linux:xr-190/linux:eth1/g' docker-compose-lab_4.yml
# sed -i 's/xrd07-gi3: null/macvlan2: null/g' docker-compose-lab_4.yml

echo "launching topology"
docker-compose -f docker-compose-lab_4.yml up --detach

echo "generate docker bridge files for tcpdump utility"
../util/nets.sh

### reset sysctl to allow routing over docker bridge instances

echo "sudo sysctl -p"
sudo sysctl -p
    