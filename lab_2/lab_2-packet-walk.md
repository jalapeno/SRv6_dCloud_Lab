

# Lab 2: SRv6 Packet Walk [15 Min]

### Description: 
This is a supplemental lab guide used to deconstruct the forwarding process of traffic through the SRv6 lab topology in this lab. 

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

In lab_1 When we ran the XRd topology setup script it called the 'nets.sh' subscript in the ~/SRv6_dCloud_Lab/util directory. The nets.sh resolved the underlying docker network IDs and wrote them to text files in the util directory. As an example link "A" in the topology has a mapped file called xrd01-xrd02 which contains the linux network id we need.

![Management Topology](/topo_drawings/management-network-medium.png)

1. Open a new ssh session on the **XRD** VM and cd into the lab's util directory:
  ```
  cd ~/SRv6_dCloud_Lab/util/
  ```
2. Start the tcpdump.sh script to monitor traffic on a link:
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
If nothing shows up on the tcpdump output try tcpdumping on the *`xrd02-xrd06`* OR *`xrd04-xrd05`* link:
Note: the ./tcpdump.sh break sequence is *ctrl-z*
  ```
  sudo ./tcpdump.sh xrd02-xrd06
  ```
  ```
  sudo ./tcpdump.sh xrd04-xrd05
  ```
Eventually pings should show up as tcpdump output. We should see SR-MPLS labels on IPv4 pings, example output below:
  ```
  cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd04-xrd05 
  sudo tcpdump -ni br-1be0f9f81cbd
  tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
  listening on br-1be0f9f81cbd, link-type EN10MB (Ethernet), capture size 262144 bytes
  21:56:27.732243 IS-IS, p2p IIH, src-id 0000.0000.0005, length 1497
  21:56:29.539521 MPLS (label 100007, exp 0, [S], ttl 254) IP 10.0.0.1 > 10.0.0.7: ICMP echo request, id 5699, seq 0, length 80
  21:56:29.541126 MPLS (label 100001, exp 0, [S], ttl 254) IP 10.0.0.7 > 10.0.0.1: ICMP echo reply, id 5699, seq 0, length 80
  ```

IPv6 pings will not invoke SRv6 encapsulation at this time. And with ECMP there's always a chance the return traffic takes a different path:
  ```
  cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd02-xrd06 
  sudo tcpdump -ni br-b50c608fd524
  tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
  listening on br-b50c608fd524, link-type EN10MB (Ethernet), capture size 262144 bytes
  21:59:25.626912 IS-IS, p2p IIH, src-id 0000.0000.0006, length 1497
  21:59:28.110163 IP6 fc00:0000:1111::1 > fc00:0000:7777::1: ICMP6, echo request, seq 0, length 60
  21:59:28.114200 IP6 fc00:0000:1111::1 > fc00:0000:7777::1: ICMP6, echo request, seq 1, length 60

  cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd04-xrd05 
  sudo tcpdump -ni br-1be0f9f81cbd
  tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
  listening on br-1be0f9f81cbd, link-type EN10MB (Ethernet), capture size 262144 bytes
  21:59:08.125911 IP6 fc00:0000:7777::1 > fc00:0000:1111::1: ICMP6, echo reply, seq 0, length 60
  21:59:08.129554 IP6 fc00:0000:7777::1 > fc00:0000:1111::1: ICMP6, echo reply, seq 1, length 60
  ```
## SRv6 forwarding





## SRv6 decapsulation to IPv4



## Return to Lab 2
Please proceed to [Lab 3](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_2/lab_2-guide.md)
