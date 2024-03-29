#/bin/sh

### run cleanup script to eliminate any stale containerlab instances

./cleanup-lab_1.sh

### launch containerlab topology

echo "launching topology"
sudo containerlab deploy -t lab_1-topology.yml

echo "generate docker bridge files for tcpdump utility"
../util/nets.sh

### reset sysctl to allow routing over bridge instances

echo "sudo sysctl -p"
sudo sysctl -p

echo "Setup complete.  XRd containers will take about 2 minutes to initialize"
