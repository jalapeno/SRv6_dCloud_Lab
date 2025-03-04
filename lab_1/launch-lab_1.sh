#!/bin/sh

echo "adding bridges"
sudo brctl addbr xrd01-amsterdam1
sudo brctl addbr xrd01-amsterdam2
sudo brctl addbr xrd02-berlin1

echo "starting VMs"
virsh start amsterdam
virsh start berlin

echo "deploying lab"
sudo clab deploy -t lab_1-topology.yml




