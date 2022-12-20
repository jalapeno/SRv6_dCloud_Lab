# SRv6 Lab 1 Guide

### Description: 
In Lab 1 the student will validate that the supplied topology is up and running and that all baseline 
connectivity is working. Second, they will validate that the pre-configured ISIS and BGP routing protocols are running and 
seeing the correct topology. Third, there will be lite SR-MPLS configuration on routers 1-7 and 
confirm PE and P roles. Last you will create basic SRv6 configuration on routers 1-7 and confirm connectivity. 

## Contents
1. [Lab Objectives](#lab-objectives)
2. [Validate Device Access](#validate-device-access)
    - [Validate to XRD VM](#validate-xrd)
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

### User Credentials
For all instances you will use the same user credentials:
```
User: cisco Password: cisco123
```

### Management Network Topology

![Lab Topology Small](/topo_drawings/management-network-medium.png)

For full size image see [LINK](/topo_drawings/management-network.png)

### Validate XRD
1. Connect to the Ubuntu VM XRD which is using Docker to host the XRD application
2. Change to the Git repository directory
    - The lab repository folder is found in the home directory ~/SRv6_dCloud_Lab/
3. Validate there are no docker containers running or docker networks for XRD
    ```
    cisco@xrd:~/SRv6_dCloud_Lab/lab_0$ docker ps
    CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
    
    cisco@xrd:~/SRv6_dCloud_Lab/lab_0$ docker network ls
    NETWORK ID     NAME      DRIVER    SCOPE
    cfd793a3a770   bridge    bridge    local
    b948b6ba5918   host      host      local
    bdf431ee7377   none      null      local
    ```
4.  Run the setup script stops any existing XRD docker containers and any XRD docker networks
    - change to the lab_0 directory
    ```
    cisco@xrd:~/SRv6_dCloud_Lab$ cd lab_0
    cisco@xrd:~/SRv6_dCloud_Lab/lab_0$
    ```
    - ``` 
    run ./setup-lab_0.sh
    ```
3. 


### Connect to Routers
