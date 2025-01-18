# Welcome to the SRv6 dCloud Lab

### Description: This repository contains lab guide, router configs, setup scripts, and other code for running through the lab.

Segment Routing over IPv6 (SRv6) is the Segment Routing implementation over an IPv6 data plane.

SRv6 introduces the Network Programming framework that enables a network operator or an application to specify a packet processing program by encoding a sequence of instructions in the IPv6 packet header. Each instruction is implemented on one or several nodes in the network and identified by an SRv6 Segment Identifier (SID) in the packet. The SRv6 Network Programming framework is defined in IETF RFC 8986 SRv6 Network Programming.

Cisco routers that run the IOS-XR operating system 7.X and newer support the SRv6 feature set. This guide walks through the basic steps to configure and test SRv6, specifically SRv6 micro-SID in a controlled lab. In addition, we use the open source Jalapeno system, which provides ways to see and use SRv6 paths through the network.


## Contents
* Repository Overview [LINK](#github-repository-overview)
* Lab Topology [LINK](#lab-topology)
* Remote Access [LINK](#remote-access)
* Project Jalapeno [LINK](#jalapeno)
* Lab 1 - XRd Topology Setup and Validation [LINK](/lab_1/lab_1-guide.md)
* Lab 2 - Config and Test Baseline SRv6 [LINK](/lab_2/lab_2-guide.md)
* Lab 3 - Config SRv6 L3VPN with SRv6-TE [LINK](/lab_3/lab_3-guide.md)
* Lab 4 - Kubernetes SRv6 with Cilium [LINK](/lab_4/lab_4-guide.md)
* Lab 5 - Project Jalapeno and Host based SRv6 [LINK](/lab_5/lab_5-guide.md)


## Github Repository Overview
Each of the labs is designed to be completed in the order presented. Lab 1 will launch our XRd topology with baseline configurations. In each subsequent lab (2-5) we'll add SRv6 configurations and make use of our SRv6 network.

### Root Directory

| File Name      | Description                                                         |
|:---------------|:--------------------------------------------------------------------|
| ansible        | Ansible scripts to update the lab at bootup                         |
| topo_drawings  | Lab diagrams folder                                                 |
| util           | Utility scripts                                                     |
| lab_1 -> lab_5 | Individual lab folders                                              |


### Individual Lab Directories
Within each lab directory you should see several files of importance:
(X = lab #)

| File Name                | Description                                                  |
|:-------------------------|:-------------------------------------------------------------|
| cleanup-lab_X.sh         | Cleans up the containerlab topology and files                |
| lab_X-topology.yml       | YAML input file for containerlab to create the topology      |
| lab_X-guide.md           | User guide for this lab                                      |


We've recently launched a whole series of SRv6 labs on github, many of which are built on XRd:

https://github.com/segmentrouting/srv6-labs

## Cisco dCloud Instances

Each lab instance is running on Cisco dCloud and is reachable via AnyConnect VPN. In the Webex Teams room for the lab we've provided a spreadsheet with a list of dCloud instances and the AnyConnect credentials necessary to access each instance. To find your dCloud instance please reference your student number provided on the handout in class.

## Lab Topology

Each lab instance consists of five virtual machines. The first VM, where we'll do most of our work, hosts seven dockerized IOS-XR routers in a simulated WAN design. Additionally there are three "client" VMs named Amsterdam, Rome, and Berlin. These VMs represent customers or consumers of our network and are each running the Ubuntu OS. The fifth VM is an Ubuntu node running Kubernetes and hosting the Jalapeno application.

![Lab Topology](/topo_drawings/overview-topology-large.png)

## Remote Access


### Virtual Machine Access Table
| VM Name        | Description              | Device Type | Access Type |   IP Address    |
|:---------------|:-------------------------|:-----------:|:-----------:|:---------------:|
| XRD            | Hosts XRd routers        | VM          | SSH         | 198.18.128.100  |
| Jalapeno       | Kubernetes + Jalapeno    | VM          | SSH         | 198.18.128.101  |
| Amsterdam      | Ubuntu client            | VM          | SSH         | 198.18.128.102  |
| Rome           | Ubuntu client            | VM          | SSH         | 198.18.128.103  |
| Berlin         | Ubuntu client            | VM          | SSH         | 198.18.128.104  |


* Use the XRD VM as an SSH jumpbox to access the XRd routers as follows:

| Device Name    | Device Type | Access Type |   IP Address  or  Hostname         |                                           
|:---------------|:------------|:------------|:----------------------------------:|                          
| xrd01          | router      | SSH         | 10.254.254.101 / clab-cleu25-xrd01 |
| xrd02          | router      | SSH         | 10.254.254.102 / clab-cleu25-xrd02 |
| xrd03          | router      | SSH         | 10.254.254.103 / clab-cleu25-xrd03 |
| xrd04          | router      | SSH         | 10.254.254.104 / clab-cleu25-xrd04 |
| xrd05          | router      | SSH         | 10.254.254.105 / clab-cleu25-xrd05 |
| xrd06          | router      | SSH         | 10.254.254.106 / clab-cleu25-xrd06 |
| xrd07          | router      | SSH         | 10.254.254.107 / clab-cleu25-xrd07 |

## Jalapeno

Project Jalapeno combines existing open source tools with some new stuff we've developed into a data collection and warehousing infrastructure intended to enable development of SDN or network service applications. Think of it as applying microservices architecture and concepts to SDN: give developers the ability to quickly and easily build microservice control planes on top of a common data collection and warehousing infrastructure. More information on Jalapeno can be found at the Jalapeno Git repository: [LINK](https://github.com/cisco-open/jalapeno/blob/main/README.md)

![jalapeno_architecture](https://github.com/cisco-open/jalapeno/blob/main/docs/img/jalapeno_architecture.png)

### Please proceed to Lab 1
[Lab 1](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_1/lab_1-guide.md)
