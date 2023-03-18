# Welcome to the World of SRv6

### Description: This repository is a learning guide for SRv6 Cisco dCloud Lab. 

SRv6 simplifies SR-MPLS networks by eliminating MPLS altogether and by relying on the native 
IPv6 header and header extension to provide the same services and flexibility as SR-MPLS, directly over the 
IPv6 data plane.

Cisco routers that run the XR operating system 7.X and newer support the SRv6 feature set. This guide walks 
through the basic steps to configure and test SR configurations in a controlled lab. In addition, Jalapeno an 
open source project provides ways to see SRv6 created paths through the network.


## Contents
* Repository Overview [LINK](#repository-overview)
* Lab Topology [LINK](#lab-topology)
* Remote Access [LINK](#remote-access)
* Project Jalapeno [LINK](#jalapeno)
* Lab 1 - XRd Topology Setup and Validation [LINK](/lab_1/lab_1-guide.md)
* Lab 2 - Config Baseline SR-MPLS and SRv6 [LINK](/lab_2/lab_2-guide.md)
* Lab 3 - Config SRv6 L3VPN with TE [LINK](/lab_3/lab_3-guide.md)
* Lab 4 - Config BMP and install Jalapeno [LINK](/lab_4/lab_4-guide.md)
* Lab 5 - A Tour of Jalapeno [LINK](/lab_5/lab_5-guide.md)
* Lab 6 - Build Your Own Cloud-Native SDN [LINK](/lab_6/lab_6-guide.md)


## Github Repository Overview
Each of the labs is designed to be completed in the order presented. Lab 1 is the baseline configurations 
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
| cleanup-lab_X.sh         | Cleans up docker environemnt                           |
| docker-compose-lab_X.yml | YAML input file used to launch docker                  |
| lab_X-topology.yml       | YAML input file for XRD to create docker compose file. |
| lab_X-guide.md           | User guide for this lab.                               |
| setup-lab_X.sh           | Calls cleanup script and launches XRD environment      | 


General instructions for building and running XRd topologies on bare-metal, VMs, AWS, etc. can be found here:
https://github.com/brmcdoug/XRd

## CLEUR Lab Session LTSPG-2212 Cisco dCloud

Each lab instance is running on Cisco dCloud, and is reachable via AnyConnect VPN. In the Webex Teams room for the lab we've provided a spreadsheet with a list of dCloud instances and the AnyConnect credentials necessary to access each instance. To find your dCloud instance please reference your student number provided on the handout in class.

The dCloud instances themselves will run until about 2pm CET (UTC +1) February 7, 2023.

## Lab Topology

This lab is based on a simulated WAN design of seven routers running in a docker instance. Each of these 
seven routers in the topology is running the XR operating system. In addition there are two client VMs named Amsterdam and Rome. Each client 
system is running the Ubuntu OS. Last is an Ubuntu VM running Kubernetes and hosting the Jalapeno application.

![Lab Topology](/topo_drawings/overview-topology-large.png)

## Remote Access


### Device Access Table
| VM Name        | Description              | Device Type | Access Type |   IP Address    |
|:---------------|:-------------------------|:-----------:|:-----------:|:---------------:|
| XRD            | Docker + XRd routers     | VM          | SSH         | 198.18.128.100  |
| Jalapeno       | Kubernettes + Jalapeno   | VM          | SSH         | 198.18.128.101  |
| Amsterdam      | Ubuntu client            | VM          | SSH         | 198.18.128.102  |
| Rome           | Ubuntu client            | VM          | SSH         | 198.18.128.103  |


* Use XRD VM as jumpbox to access the XRd routers as follows:

| Device Name    | Device Type | Access Type |   IP Address    |                                           
|:---------------|:------------|:------------|:---------------:|                          
| xrd01           | router      | SSH         | 10.254.254.101  |
| xrd02           | router      | SSH         | 10.254.254.102  |
| xrd03           | router      | SSH         | 10.254.254.103  |
| xrd04           | router      | SSH         | 10.254.254.104  |
| xrd05           | router      | SSH         | 10.254.254.105  |
| xrd06           | router      | SSH         | 10.254.254.106  |
| xrd07           | router      | SSH         | 10.254.254.107  |

## Jalapeno

Project Jalapeno combines existing open source tools with some new stuff we've developed into a data collection and warehousing infrastructure intended to enable development of SDN or network service applications. Think of it as applying microservices architecture and concepts to SDN: give developers the ability to quickly and easily build microservice control planes on top of a common data collection and warehousing infrastructure. More information on Jalapeno can be found at the Jalapeno Git repository: [LINK](https://github.com/cisco-open/jalapeno/blob/main/README.md)

![jalapeno_architecture](https://github.com/cisco-open/jalapeno/blob/main/docs/diagrams/jalapeno_architecture.png)


