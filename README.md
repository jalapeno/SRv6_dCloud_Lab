# SRv6 dCloud Lab Guide

### Description: This repository contains lab configurations, instructions, and scripts to learn SR-MPLS and 
SRv6 configurations on Cisco XR routers. In addition it features content on the Jalpaneo telemetry project.

## Contents
1. [Lab One Guide](/lab_1/lab_1-guide.md)

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


