# SRv6 dCloud Lab Guide

### Description: This repository is a learning guide for SRv6 Cisco dCloud Lab. 
Cisco Routers that run the XR operating system 7.X and newer support the SRv6 feature set. This guide walks 
through the basic steps to configure and test SR configurations in a controlled lab. In addition, Jalapeno an 
open source project provides ways to see SRv6 created paths through the network.

## Contents
* Lab 1 - Config Baseline SR-MPLS and SRv6 [LINK](/lab_1/lab_1-guide.md)
* Lab 2 - Config SRv6 with L3VPN [LINK](/lab_2/lab_2-guide.md)
* Lab 3 - Config SRv6 with TE [LINK](/lab_3/lab_3-guide.md)
* Lab 4 - Config BMP and install Jalapeno [LINK](/lab_4/lab_4-guide.md)
* Lab 5 - Config Jalapeno [LINK](/lab_5/lab_5-guide.md)
* Lab 6 - Build Cloud-Native SDN [LINK](/lab_6/lab_6-guide.md)
* Understanding Lab Scripts (#scripts)


## Scripts
Each of the labs is designed to be completed in the order presented. Lab 0 is the baseline configurations 
needed to build the starting topology and launch the XRd and extended environment.

Within each lab directory you should see several files of importance :
(X = lab #)
```
| File Name                | Description                                            |
|:-------------------------|:-------------------------------------------------------|
| cleanup-lab_X.sh         | Cleans up docker environemtn                           |
| docker-compose-lab_1.yml | YAML input file used to launch docker                  |
| lab_X-topology.yml       | YAML input file for XRD to create docker compose file. |
| lab_X-guide.md           | User guide for this lab.                               |
| setup-lab_X.sh           | Calls cleanup script and launches XRD environment      | 
```

General instructions for building and running XRd topologies on bare-metal, VMs, AWS, etc. can be found here:
https://github.com/brmcdoug/XRd

Scripts in this top level directory:
```
./host-check    ## Runs an analysis verify whether XRd can run on your host, and how many instances it'll support
  
./xr-compose ## generates a docker-compose yml based upon the input (-f) topology yml file

Example:
./xr-compose -f docker-compose-lab_1.yml -li ios-xr/xrd-control-plane:7.8.1
```
However, at the beginning of the CLEU lab we'll launch the topology using the setup script found in the lab_0 directory.  
  
After lauching the topology, check containers: 
```
docker ps
```
Note, it will take a couple minutes for the containers to build, so cli won't be immediately available:

To access XRd cli:
```
docker exec -it xrd01 /pkg/bin/xr_cli.sh

or

ssh cisco@10.254.254.101    ## xrd01
ssh cisco@10.254.254.102    ## xrd02
etc.
```

### Special bonus:

#### 27 node topology
Tested on bare metal with 32 vCPU and 96G of memory.
It does require some additional tuning:

1. Increase Docker default-address-pools by adding something like following to /etc/docker/daemon.json

```
{
  "default-address-pools" : [
    {
      "base" : "172.17.0.0/12",
      "size" : 20
    },
    {
      "base" : "192.168.0.0/16",
      "size" : 24
    }
  ]
}
```

2. Increase the docker-compose parallel limit and timeout threshold:
```
export COMPOSE_PARALLEL_LIMIT=1000
export DOCKER_CLIENT_TIMEOUT=600
export COMPOSE_HTTP_TIMEOUT=600

```

3. Boost /etc/sysctl.conf inotify params even further
```
fs.inotify.max_user_watches=131072
fs.inotify.max_user_instances=131072
```


