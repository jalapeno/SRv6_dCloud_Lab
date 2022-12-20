# SRv6 dCloud Lab Guide

### Description: This repository is a learning guide for SRv6 Cisco dCloud Lab. 
Cisco Routers that run the XR operating system 7.X and newer support the SRv6 feature set. This guide walks 
through the basic steps to configure and test SR configurations in a controlled lab. In addition, Jalapeno an 
open source project provides ways to see SRv6 created paths through the network.

## Contents
* Repository Overview [LINK](#repository-overview)
* Lab Topology [LINK](#topology)
* Remote Access [LINK](#remote-access)
* Lab 1 - Config Baseline SR-MPLS and SRv6 [LINK](/lab_1/lab_1-guide.md)
* Lab 2 - Config SRv6 with L3VPN [LINK](/lab_2/lab_2-guide.md)
* Lab 3 - Config SRv6 with TE [LINK](/lab_3/lab_3-guide.md)
* Lab 4 - Config BMP and install Jalapeno [LINK](/lab_4/lab_4-guide.md)
* Lab 5 - Config Jalapeno [LINK](/lab_5/lab_5-guide.md)
* Lab 6 - Build Cloud-Native SDN [LINK](/lab_6/lab_6-guide.md)


## Repository Overview
Each of the labs is designed to be completed in the order presented. Lab 0 is the baseline configurations 
needed to build the starting topology and launch the XRd and extended environment.

### Root Directory

| File Name                | Description                                                    |
|:-------------------------|:---------------------------------------------------------------|
| host_check               | Runs an analysis verify whether XRd can run on your host       |
| xr-compose               | Inputs a defined XRD YAML file and creates docker compose file |

```
Example:
./xr-compose -f docker-compose-lab_1.yml -li ios-xr/xrd-control-plane:7.8.1
```

### Individual Lab Directories
Within each lab directory you should see several files of importance :
(X = lab #)

| File Name                | Description                                            |
|:-------------------------|:-------------------------------------------------------|
| cleanup-lab_X.sh         | Cleans up docker environemtn                           |
| docker-compose-lab_1.yml | YAML input file used to launch docker                  |
| lab_X-topology.yml       | YAML input file for XRD to create docker compose file. |
| lab_X-guide.md           | User guide for this lab.                               |
| setup-lab_X.sh           | Calls cleanup script and launches XRD environment      | 


General instructions for building and running XRd topologies on bare-metal, VMs, AWS, etc. can be found here:
https://github.com/brmcdoug/XRd

## Lab Topology

## Remote Access



