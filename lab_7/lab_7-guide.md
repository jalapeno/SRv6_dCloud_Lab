# Lab 7 - Build your own SDN App (BYO-SDN-App)

The goal of the Jalapeno model is to enable applications to directly control their network experience. We envision a process where the application or endpoint requests some Jalapeno network service for its traffic. The Jalapeno network-service queries the DB and provides a response, which includes an SR-MPLS or SRv6 SID stack. The application or endpoint would then encapsulate its own outbound traffic. The encapsulated traffic reaches the SR/SRv6 transport network and is statelessly forwarded per the SR/SRv6 encapsulation, thus executing the requested network service treatment. Essentially the application or endpoint will be executing its own SR/SRv6 network program.

Both the Rome and Amsterdam VM's are pre-loaded with a python client that will execute our Jalapeno network service per the process described above. After the client has run the VM will self-encapsulate outbound traffic and the xrd network will forward traffic per the SR/SRv6 encap.

In order to forward inbound labeled packets from the Rome and Amsterdam VMs we'll need to enable MPLS forwarding on xrd01's and xrd07's VM-facing interfaces:

1. Enable MPLS forwarding on the VM-facing interfaces on both xrd01 and xrd07: 

```
mpls static
 int gigabitEthernet 0/0/0/0
 commit
```
Validate MPLS forwarding is enabled:
```
show mpls interface
```
Expected output:
```
Fri Dec 23 23:24:11.146 UTC
Interface                  LDP      Tunnel   Static   Enabled 
-------------------------- -------- -------- -------- --------
GigabitEthernet0/0/0/0     No       No       Yes      Yes
GigabitEthernet0/0/0/1     No       No       No       Yes
GigabitEthernet0/0/0/2     No       No       No       Yes
```

Now we're ready to work from the Rome VM. Please proceed to [lab_7-Rome.md](https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_7/lab_7-Rome.md)



Note: the python code in this lab has a dependency on the python-arango module. The module has been preinstalled on both the Rome and Amsterdam VMs, however, if one wishes to recreate this lab in their own environment, any client node will need to install the module:
```
sudo apt install python3-pip
pip install python-arango 
```