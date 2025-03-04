#!/bin/sh

echo "adding bridges"
sudo brctl addbr amsterdam1
sudo brctl addbr amsterdam2
sudo brctl addbr berlin1
sudo ip link set amsterdam1 up
sudo ip link set amsterdam2 up
sudo ip link set berlin1 up

echo "starting VMs"
virsh start amsterdam
virsh start berlin

echo "deploying lab"
sudo clab deploy -t lab_1-topology.yml




