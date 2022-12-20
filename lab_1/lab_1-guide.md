# SRv6 Lab 1 Guide

### Description: 
In Lab 1 the student will validate that the supplied topology is up and running and that all baseline 
connectivity is working. Second, they will validate that the pre-configured ISIS and BGP routing protocols are running and 
seeing the correct topology. Third, there will be lite SR-MPLS configuration on routers 1-7 and 
confirm PE and P roles. Last you will create basic SRv6 configuration on routers 1-7 and confirm connectivity. 

## Contents
1. [Lab Objectives](#lab-objectives)
2. [Validate Device Access](#validate-device-access)
    - [Connect to VMs](#connect-to-vms)
    - [Connect to Routers](#connect-to-routers)
3. Validate ISIS Topology
4. Validate BGP Topology
5. Configure and validate SR-MPLS
6. Configure and validate SRv6


## 1. Lab Objectives
The student upon completion of Lab 1 should have achieved the following objectives

    * Access to all devices in the lab
    * Understanding of the lab topology and components
    * Understanding of basic configuration for SR-MPLS
    * Understanding of basic configuration for SRv6
   

## 2. Validate Device Access

Device access for this lab is primarly through SSH. All of the VMs within this toplogy can be accessed once you connect through Cisco AnyConnect VPN to the dCloud environment. Please see the management topology network diagram below. In addition their are seven instances of XR routers running in containers on the VM host XRD. The XRD VM acts as a jumpbox for these router containers. For router access you will need to SSH into the XRD VM and then initiate a separate SSH session to each of the routers. The XRD VM is configured for DNS resolution for each router name to save time.

### Management Network Topology

![Lab Topology](/topo_drawings/management-network.png)


![Lab Topology Small](/topo_drawings/management-network-small.png)

### Connect to VMs


### Connect to Routers
