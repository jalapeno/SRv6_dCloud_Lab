

# Lab 2: SRv6 uSID Packet Walk [15 Min]

### Description: 
This is a supplemental lab guide used to deconstruct the forwarding process of traffic through the SRv6 lab topology in this lab. In Lab 2 we are setting up a SRv6 topology using the global forwarding table for forwarding packets in the network. This is distinct from Lab 3 where we will add the virtualization concept of L3VPN + SRv6.

## Contents
- [Lab 2: SR-MPLS and SRv6 Install \[20 Min\]](#lab-2-sr-mpls-and-srv6-install-20-min)
    - [Description:](#description)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [IPv4 encapsulation to SRv6](#ipv4-encapsulation-to-srv6)
  - [SRv6 forwarding](#srv6-forwarding)
  - [SRv6 decapsulation to IPv4](#srv6-decapsulation-to-ipv4)
- [Return to Lab 2](#return-to-lab-2)
  

## Lab Objectives
The student upon completion of Lab 2 should have achieved the following objectives:

* Understand how standard IPv4 or IPv6 packets are encapsulated with SRv6 headers
* Understand the forwarding behavior of SRv6 enabled routers
* Understand how SRv6 routers decapsulate and forward traffic as an IPv4 or IPv6 packet
* Understand how IPv6 only routers can participate in SRv6 networks.


## IPv4 Encapsulation to SRv6

In Lab 2 this step occurs in Router 1. On ingress from the Amsterdam node we receive an IPv4 packet that needs forwarding to Rome. We will walk through the process of determining that SRv6 encapsulation is required and lookup process.

![Router 1 Topology](/topo_drawings/ltrspg-2212-packet-walk-r1.png)

1. Router 1 receives IPv4 packet from Amsterdam and we parse the IPv4 DA address of the packet.
    ```
    cd ~/SRv6_dCloud_Lab/util/
    ```
2. Lookup of the IPv4 DA address in the global routing table and show LPM match.
    ```
    ./tcpdump.sh xrd05-xrd06
    ```
3. LPM match from step 2 is used to lookup the IP CEF forwarding information.
    ```
    ping 10.0.0.7 source lo0
    ```
    ```
    ping fc00:0000:7777::1 source lo0
    ```
4. Create SRv6 header and append to original packet and forward to Router 2.
    '''
    '''


   
## SRv6 forwarding

In lab_1 When we ran the XRd topology setup script it called the 'nets.sh' subscript in the ~/SRv6_dCloud_Lab/util directory. The nets.sh resolved the underlying docker network IDs and wrote them to text files in the util directory. As an example link "A" in the topology has a mapped file called xrd01-xrd02 which contains the linux network id we need.

![Router 1 Topology](/topo_drawings/ltrspg-2212-packet-walk-r3.png)

1. Step #1 insert stuff
    ```
    cd ~/SRv6_dCloud_Lab/util/
    ```
2. Step #2 insert stuff
    ```
    ./tcpdump.sh xrd05-xrd06
    ```
3. Run some pings from **xrd01** to **xrd07**:
    ```
    ping 10.0.0.7 source lo0
    ```
    ```
    ping fc00:0000:7777::1 source lo0
    ```

## SRv6 decapsulation to IPv4

In lab_1 When we ran the XRd topology setup script it called the 'nets.sh' subscript in the ~/SRv6_dCloud_Lab/util directory. The nets.sh resolved the underlying docker network IDs and wrote them to text files in the util directory. As an example link "A" in the topology has a mapped file called xrd01-xrd02 which contains the linux network id we need.

![Router 1 Topology](/topo_drawings/ltrspg-2212-packet-walk-r7.png)

1. Step #1 insert stuff
    ```
    cd ~/SRv6_dCloud_Lab/util/
    ```
2. Step #2 insert stuff
    ```
    ./tcpdump.sh xrd05-xrd06
    ```
3. Run some pings from **xrd01** to **xrd07**:
    ```
    ping 10.0.0.7 source lo0
    ```
    ```
    ping fc00:0000:7777::1 source lo0
    ```

## Return to Lab 2
Please proceed to [Lab 2](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_2/lab_2-guide.md)