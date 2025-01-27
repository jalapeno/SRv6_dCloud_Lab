## Lab 6: Host-Based SR/SRv6 and building your own SDN App

### Description
The goals of the Jalapeno project are:

1. Enable applications to directly control their network experience by giving them the ability to apply SRv6 policies/encapsulations to their own traffic
   
2. Enable developers to quickly and easily build network control or SDN Apps that client applications may use achieve goal #1 

We won't claim to be professional developers, but using Jalapeno and just a few hours of python coding we were able to build an SRv6 SDN App called **"jalapeno.py"**. Our App can program SRv6-TE routes/policies on Linux hosts/VMs and on [VPP](https://fd.io/). Hopefully soon we'll be able to do the same for Cilium!

Its not a very sophisticated App, but it gives a sense of the power and possibilities when combining *SRv6 and host-based or cloud-native networking*. 

And if the two of us knuckleheads can cobble together a functional SDN App in a couple of hours, imagine what a group of real developers could do in a few short weeks!

Why host-based SRv6? 

* We get tremendous control of the SRv6 SIDs and our encapsulation depth isn't subject to ASIC limitations
* With host-based SRv6 traffic reaches the transport network already encapsulated, thus the ingress PE or SRv6-TE headend doesn't need all the resource intense policy configuration; they just statelessly forward traffic per the SRv6 encapsulation or Network Program
* We could extend SRv6 into the Cloud! Or to IoT devices or other endpoints connected to the physical network...
 
We feel this ability to perform SRv6 operations at the host or other endpoint is a game changer which opens up enormous potential for innovation!

## Contents
- [Lab 6: Host-Based SR/SRv6 and building your own SDN App](#lab-6-host-based-srsrv6-and-building-your-own-sdn-app)
  - [Description](#description)
- [Contents](#contents)
- [Lab Objectives](#lab-objectives)
- [Rome VM: Segment Routing \& SRv6 on Linux](#rome-vm-segment-routing--srv6-on-linux)
  - [Preliminary steps for SR/SRv6 on Rome VM](#preliminary-steps-for-srsrv6-on-rome-vm)
  - [jalapeno.py:](#jalapenopy)
    - [fix the writeup of this section](#fix-the-writeup-of-this-section)
- [Rome Network Services](#rome-network-services)
  - [Get All Paths](#get-all-paths)
  - [Least Utilized Path](#least-utilized-path)
  - [Low Latency Path](#low-latency-path)
  - [Low Latency Re-Route](#low-latency-re-route)
  - [Data Sovereignty Path](#data-sovereignty-path)
- [Amsterdam VM](#amsterdam-vm)
  - [POC host-based SRv6 and SR-MPLS SDN using the VPP dataplane](#poc-host-based-srv6-and-sr-mpls-sdn-using-the-vpp-dataplane)
  - [jalapeno.py on Amsterdam:](#jalapenopy-on-amsterdam)
- [Amsterdam Network Services](#amsterdam-network-services)
  - [Get All Paths](#get-all-paths-1)
  - [Least Utilized Path](#least-utilized-path-1)
  - [Low Latency Path](#low-latency-path-1)
  - [Data Sovereignty Path](#data-sovereignty-path-1)
  - [You have reached the end of LTRSPG-2212, hooray!](#you-have-reached-the-end-of-ltrspg-2212-hooray)

## Lab Objectives
The student upon completion of Lab 6 should have achieved the following objectives:

* Understanding of the SRv6 stack available in Linux
* Understanding the use of VPP as a host-based SRv6 forwarding element 
* How to query Jalapeno API with Python for network topology and SRv6 data
* Using Python to craft specific SRv6 headers for traffic steering or other use cases
* Using Python to to program SRv6 forwarding entries on a Linux host

> [!NOTE]
> The python code used in this lab has a dependency on the python-arango module. The module has been preinstalled on both the Rome and Amsterdam VMs, however, if one wishes to recreate this lab in their own environment, any client node will need to install the module. We also suggest upgrading the http *'requests'* library as that will eliminate some cosmetic http error codes.
> For reference:
```
sudo apt install python3-pip
pip install python-arango 
pip3 install --upgrade requests
```

## Rome VM: Segment Routing & SRv6 on Linux

The Rome VM is simulating a user host or endpoint and will use its Linux dataplane to perform SRv6 traffic encapsulation:

 - Linux SRv6 route reference: https://segment-routing.org/index.php/Implementation/Configuration

### Preliminary steps for SR/SRv6 on Rome VM
   1.  Login to the Rome VM
   ```
   ssh cisco@198.18.128.103
   ```

   2. On the Rome VM cd into the lab_6 directory where the jalapeno.py client resides:
   ```
   cd ~/SRv6_dCloud_Lab/lab_6/python
   ```
   3. Get familiar with files in the directory; specifically:
   ```
   cat rome.json                 <------- data jalapeno.py will use to execute its query and program its SRv6 route
   cat cleanup_rome_routes.sh    <------- script to cleanup any old SRv6 routes
   cat jalapeno.py               <------- python app that takes cmd line args to request/execute an SRv6 network service
   ls netservice/                <------- contains python libraries available to jalapeno.py for calculating SRv6 SIDs

   ```
   4. For SRv6 outbound encapsulation we'll need to set Rome's SRv6 source address:

   ```
   sudo ip sr tunsrc set fc00:0:107:1::1
   ```

### jalapeno.py:
Both the Rome and Amsterdam VM's are pre-loaded with the *`jalapeno.py`* App. When we run `jalapeno.py` it will program a local route/policy with SRv6 encapsulation, which will allow the VM to *`self-encapsulate`* its outbound traffic. The XRd network will then statelessly forward the traffic per the SRv6 encapsulation.

 `jalapeno.py's` currently supported network services are: 

 - Low Latency Path
 - Least Utilized Path
 - Data Sovereignty Path
 - Get All Paths (informational only)
 
 When executed `jalapeno.py` passes its service request as an API call to execute a Shortest Path query on the graph database. The database performs a graph-traversal, as seen in lab 5, and responds with a dataset reflecting the shortest path per the parameters of the query. `jalapeno.py` receives the data and constructs a local SRv6 route/policy for any traffic it would send to the destination.

Currently `jalapeno.py` operates as a CLI tool, which expects to see a set of command line arguments specifying network service (-s), encapsulation (-e), and input a json file which contains source and destination info and a few other items.

For ease of use the currently supported network services are abbreviated: 

 - gp = get_all_paths
 - ll = low_latency
 - lu = least_utilized
 - ds = data_sovereignty

1. On the Rome VM cd into the lab_6 python directory and access client help with the *-h* argument:
    ```
    cd ~/SRv6_dCloud_Lab/lab_6/python
    python3 jalapeno.py -h
    ``` 
    Expected output:
    ```
    cisco@rome:~/SRv6_dCloud_Lab/lab_6/python$ python3 jalapeno.py -h
    usage: Jalapeno client [-h] [-e E] [-f F] [-s S]

    takes command line input and calls path calculator functions

    optional arguments:
      -h, --help  show this help message and exit
      -e E        encapsulation type <sr> <srv6>
      -f F        json file with src, dst, parameters
      -s S        requested network service: ll = low_latency, lu = least_utilized, ds = data_sovereignty, gp = get_paths

    jalapeno.py -f <json file> -e <sr or srv6> -s <ll, lu, ds, or gp>
    ```

    Example command with network-service arguments asking for the least utilized srv6 path to the destination specified in rome.json:
    ```
    python3 jalapeno.py -f rome.json -e srv6 -s lu
    ```

> [!NOTE]
> The jalapeno.py supports both SRv6 and SR-MPLS, however, we don't have SR-MPLS configured in our lab so we'll only be using the *`-e srv6`* encapsulation option.

#### fix the writeup of this section

*`jalapeno.py's`* network service modules are located in the lab_6 *`python/netservice/`* directory. When invoked `jalapeno.py` feeds the source and destination prefixes from the json file to the *`src_dst.py`* module, which calls the API and returns the prefixes' database ID info. `jalapeno.py` then runs the selected network service module (gp, ll, lu, or ds). The network service module queries and calculates an SRv6 uSID or SR label stack, which will satisfy the network service request. The netservice module then calls the *`add_route.py`* module to create the local SR or SRv6 route or policy.

## Rome Network Services
### Get All Paths

The Get All Paths Service will query the DB for all paths up to 6-hops in length between a pair of source and destination prefixes.

1. Run the Get All Paths 'gp' service:
    ``` 
    python3 jalapeno.py -f rome.json -s gp -e srv6
    ```
      - Sample command line output:
    ```
    cisco@rome:~/SRv6_dCloud_Lab/lab_6/python$ python3 jalapeno.py -f rome.json -s gp -e srv6

    Get All Paths Service
    number of paths found:  4

    path locator list:  ['fc00:0:7777::', 'fc00:0:4444::', 'fc00:0:5555::', 'fc00:0:1111::']
    srv6 sid for this path:  fc00:0:7777:4444:5555:1111::

    path locator list:  ['fc00:0:7777::', 'fc00:0:6666::', 'fc00:0:2222::', 'fc00:0:1111::']
    srv6 sid for this path:  fc00:0:7777:6666:2222:1111::

    path locator list:  ['fc00:0:7777::', 'fc00:0:6666::', 'fc00:0:5555::', 'fc00:0:1111::']
    srv6 sid for this path:  fc00:0:7777:6666:5555:1111::

    path locator list:  ['fc00:0:7777::', 'fc00:0:4444::', 'fc00:0:3333::', 'fc00:0:2222::', 'fc00:0:1111::']
    srv6 sid for this path:  fc00:0:7777:4444:3333:2222:1111::

    All paths data from unicast_prefix_v4/20.0.0.0_24_10.0.0.7 to unicast_prefix_v4/10.101.2.0_24_10.0.0.1 logged to log/get_paths.json
    ```
    - The code contains a number of console logging instances that are commented out, and some that are active (hence the output above). Note this line which provides a summary of the relevant paths by outputing the SRv6 locators along each path:

      https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_6/python/netservice/gp.py#L46


    - All the jalapeno network services will output some data to the console. More verbose data will be logged to the lab_6/python/log directory. Check log output:
    ```
    more log/get_paths.json
    ```
    - We can expect to see a json file with source, destination, and path data which includes srv6 locators and sids

2. Optional: try increasing the number of hops the graph may traverse:

    ```
    for v, e, p in 1..8 outbound
    ```
    Save the file and re-run the script. You should see 8 total path options in the command line output and log.

### Least Utilized Path
Many segment routing and other SDN solutions focus on the low latency path as their primary use case. We absolutely feel low latency is an important network service, especially for real time applications. However, we believe one of the use cases which deliver the most bang for the buck is "Least Utilized Path". The idea behind this use case is that the routing protocol's chosen best path is very often *The Actual Best Path*. Because of this `jalapeno.py's` *`Least Utilized`* service looks to steer lower priority traffic (backups, content replication, etc.) to lesser used paths and preserve the routing protocol's "best path" for higher priority traffic.

1. Cleanup Rome's routes and execute the least utilized path service with SRv6 encapsulation
    ```
    ./cleanup_rome_routes.sh 
    python3 jalapeno.py -f rome.json -e srv6 -s lu
    ```
    Expected console output should include some log info from the script, and output of linux *ip route* command showing the newly added route with SRv6 encapsulation:
    ```
    cisco@rome:~/SRv6_dCloud_Lab/lab_6/python$ python3 jalapeno.py -f rome.json -e srv6 -s lu

    Least Utilized Service
    locator list for least utilized path:  ['fc00:0:7777::', 'fc00:0:6666::', 'fc00:0:2222::', 'fc00:0:1111::']
    egress node locator:  fc00:0:1111::
    end.dt SID:  ['fc00:0:1111:e007::']
    srv6 sid:  fc00:0:7777:6666:2222:1111:e007::

    adding linux SRv6 route: ip route add 10.101.2.0/24 encap seg6 mode encap segs fc00:0:7777:6666:2222:1111:e007:: dev ens192
    RTNETLINK answers: File exists

    Show Linux Route Table: 
    default via 198.18.128.1 dev ens160 proto static 
    10.0.0.0/24 via 10.107.1.2 dev ens192 proto static 
    10.1.1.0/24 via 10.107.1.2 dev ens192 proto static 
    10.101.1.0/24 via 10.107.1.2 dev ens192 proto static 
    10.101.2.0/24  encap seg6 mode encap segs 1 [ fc00:0:6666:2222:1111:e004:: ] dev ens192 scope link  <--------
    10.101.3.0/24 via 10.107.2.2 dev ens224 proto static 
    10.107.1.0/24 dev ens192 proto kernel scope link src 10.107.1.1 
    10.107.2.0/24 dev ens224 proto kernel scope link src 10.107.2.1 
    198.18.128.0/18 dev ens160 proto kernel scope link src 198.18.128.103 
    ```

2. Optional: the logfile output will show more detailed info:
    ```
    cat log/least_util.json
    ```

3. Run a ping test 
 - Open up a second ssh session to the Rome VM
```
ssh cisco@198.18.128.103
```
 - Start tcpdump on the 2nd ssh session. This will capture packets outbound from Rome VM going toward xrd07:
```
sudo tcpdump -lni ens192
```
 - Return to the first Rome ssh session and ping Amsterdam with Rome source address 20.0.0.1. The "-i .3" argument sets the ping interval to 300ms
```
ping 10.101.2.1 -I 20.0.0.1 -i .3
```
> [!NOTE]
> As of CLEU25 there is occasionally an issue where IPv6 neighbor instances timeout between Rome Linux and the XRd MACVLAN attachment on *`xrd07`*. So if your ping doesn't work try ssh'ing into *`xrd07`* and ping *`Rome`*. A successful ping should 'wake up' the IPv6 neighborship.

On *`xrd07`*:  
```
ping fc00:0:107:1::1
```
Output:
```
RP/0/RP0/CPU0:xrd07#ping fc00:0:107:1::1
Wed Feb  1 04:21:15.980 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to fc00:0:107:1::1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/5 ms
```

4. Retry the Rome to Amsterdam ping test:
```
ping 10.101.2.1 -I 20.0.0.1 -i .3
```

5. Check the Rome tcpdump to validate traffic is encapsulated with the SRv6 SID. Expected output will be something like:
```
cisco@rome:~$ sudo tcpdump -lni ens192
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on ens192, link-type EN10MB (Ethernet), capture size 262144 bytes
18:04:14.873127 IP6 fc00:0:107:1::1 > fc00:0:7777:6666:2222:1111:e007:0: srcrt (len=2, type=4, segleft=0[|srcrt]
18:04:14.945878 IP 10.101.2.1 > 20.0.0.1: ICMP echo reply, id 3, seq 1, length 64
18:04:15.173485 IP6 fc00:0:107:1::1 > fc00:0:7777:6666:2222:1111:e007:0: srcrt (len=2, type=4, segleft=0[|srcrt]
18:04:15.241699 IP 10.101.2.1 > 20.0.0.1: ICMP echo reply, id 3, seq 2, length 64
```

6. Return to an SSH session on the XRD VM and use tcpdump.sh <xrd0x-xrd0y>" to capture packets along the path from Rome VM to Amsterdam VM. Given the SRv6 Micro-SID combination seen above, we'll monitor the linux bridges linking *`xrd07`* to *`xrd06`*, *`xrd06`* to *`xrd02`*, then *`xrd02`* to *`xrd01`*:
 - restart the ping if it is stopped

*Note: feel free to just spot check 1 or 2 of these:

```
netns tcpdump 
```

 - Example output for the link between *`xrd06`* to *`xrd02`* is below. Note how *`xrd06`* has performed SRv6 micro-SID shift-and-forward on the destination address. Also note how the return traffic is taking SR-MPLS transport (currently). 
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd02-xrd06
sudo tcpdump -lni br-07e02174172b
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on br-07e02174172b, link-type EN10MB (Ethernet), capture size 262144 bytes
23:30:45.978380 IP6 fc00:0:107:1::1 > fc00:0:2222:1111:e007::: srcrt (len=2, type=4, segleft=0[|srcrt]
23:30:46.010720 MPLS (label 100007, exp 0, ttl 61) (label 24010, exp 0, [S], ttl 62) IP 10.101.2.1 > 20.0.0.1: ICMP echo reply, id 4, seq 9, length 64
23:30:46.279814 IP6 fc00:0:107:1::1 > fc00:0:2222:1111:e007::: srcrt (len=2, type=4, segleft=0[|srcrt]
23:30:46.315159 MPLS (label 100007, exp 0, ttl 61) (label 24010, exp 0, [S], ttl 62) IP 10.101.2.1 > 20.0.0.1: ICMP echo reply, id 4, seq 10, length 64
```

### Low Latency Path
The Low Latency Path service will calculate an SRv6 encapsulation instruction for sending traffic over the lowest latency path from a source to a given destination. The procedure for testing/running the Low Latency Path service is the same as the one we followed with Least Utilized Path. 

The low latency path from Rome to Amsterdam should follow the path shown in the below diagram. Traffic should flow in the direction of **xrd07** -> **xrd06** -> **xrd05** -> **xrd01**

![Low Latency Path](/topo_drawings/low-latency-path.png)

For full size image see [LINK](/topo_drawings/low-latency-path.png)

1. Low latency SRv6 service on Rome VM:
    ```
    ./cleanup_rome_routes.sh 
    python3 jalapeno.py -f rome.json -e srv6 -s ll
    ping 10.101.2.1 -I 20.0.0.1 -i .3
    ```
    1. As with Least Utilized Path we can run the tcpdump scripts On the XRD VM to see our SRv6 encapsulated traffic traverse the network with uSID shift-and-forward in action (feel free to spot check): 
    ```
    ./tcpdump.sh xrd06-xrd07
    ```
    ```
    ./tcpdump.sh xrd05-xrd06
    ```
    ```
    ./tcpdump.sh xrd01-xrd05
    ```

### Low Latency Re-Route
Now we are going to simulate a recalculation of the SRv6 topology. The *Sub-Standard Construction Company* has taken out fiber link "G" with a backhoe. Luckily you have paid for optical path redundancy and the link has failed to a geographicaly different path. The result though is that the primary path latency of *5ms* has increased to *25 ms*. This should cause a new low latency route. Time to test it out!

![Low Latency Path](/topo_drawings/low-latency-alternate-path.png)

For full size image see [LINK](/topo_drawings/low-latency-alternate-path.png)

1. Link "G" needs to have the latency in your topology updated. We will use the Python script located in /lab_6/python/set_latency.py to change the link latency in the lab and then update the ArangoDb topology database with the new value. Set latency has two cli requirements -l (link letter) [A,B,C,D,E,F,G,H,I] and -ms (milliseconds latency) xxx values.

    On **XRD VM** run the command
    ```
    cd /home/cisco/SRv6_dCloud_Lab/lab_6/python
    python3 set_latency.py -l G -ms 25
    ```
    * Note: if your ping is still running you should see its reply time increase from around 55ms to around 85ms

2. Re-run the Low latency SRv6 service on **Rome VM**. After running your ping time should decrease to around 70ms:
    ```
    ./cleanup_rome_routes.sh 
    python3 jalapeno.py -f rome.json -e srv6 -s ll
    ping 10.101.2.1 -I 20.0.0.1 -i .3
    ```

3. Run an iPerf3 test from Rome to Amsterdam and watch our network crush 250Kbps!
   
   First ssh to Amsterdam VM:
    ```
    ssh cisco@198.18.128.102
    ```

    Then activate the iPerf3 server:
    ```
    iperf3 -s -D
    ```

    Start iPerf3 traffic on Rome VM:
    ```
    iperf3 -c 10.101.2.1 -B 20.0.0.1 -w 2700 -M 2700
    ```
    ```
    cisco@rome:~$  iperf3 -c 10.101.2.1 -B 20.0.0.1 -w 2700 -M 2700
    Connecting to host 10.101.2.1, port 5201
    [  5] local 20.0.0.1 port 56113 connected to 10.101.2.1 port 5201
    [ ID] Interval           Transfer     Bitrate         Retr  Cwnd
    [  5]   0.00-1.00   sec  22.6 KBytes   185 Kbits/sec    2   7.42 KBytes       
    [  5]   1.00-2.00   sec  33.9 KBytes   278 Kbits/sec    0   7.42 KBytes       
    [  5]   2.00-3.00   sec  31.8 KBytes   261 Kbits/sec    0   7.42 KBytes       
    [  5]   3.00-4.00   sec  33.9 KBytes   278 Kbits/sec    0   7.42 KBytes       
    [  5]   4.00-5.00   sec  33.9 KBytes   278 Kbits/sec    0   7.42 KBytes       
    [  5]   5.00-6.00   sec  31.8 KBytes   261 Kbits/sec    0   7.42 KBytes       
    [  5]   6.00-7.00   sec  33.9 KBytes   278 Kbits/sec    0   7.42 KBytes       
    [  5]   7.00-8.00   sec  31.8 KBytes   261 Kbits/sec    0   7.42 KBytes       
    [  5]   8.00-9.00   sec  31.8 KBytes   261 Kbits/sec    0   7.42 KBytes       
    [  5]   9.00-10.00  sec  33.9 KBytes   278 Kbits/sec    0   7.42 KBytes       
    - - - - - - - - - - - - - - - - - - - - - - - - -
    [ ID] Interval           Transfer     Bitrate         Retr
    [  5]   0.00-10.00  sec   320 KBytes   262 Kbits/sec    2             sender
    [  5]   0.00-10.06  sec   319 KBytes   259 Kbits/sec                  receiver

    iperf Done. 
    ```


### Data Sovereignty Path
The Data Sovereignty service enables the user or application to steer their traffic through a path or geography that is considered safe per a set of legal guidelines or other regulatory framework. In our case the *`DS`* service allows us to choose a country (or countries) to avoid when transmitting traffic from a source to a given destination. The country to avoid is specified as a country code in the *`rome.json`* and *`amsterdam.json`* files. In our testing we've specified that traffic should avoid France (FRA) - no offense, its just the easiest path in our topology to demonstrate. *`xrd06`* is located in Paris, so all requests to the DS service should produce a shortest-path result that avoids *`xrd06`*.

The procedure for testing/running the Data Sovereignty Service is the same as the one we followed with Least Utilized and Low Latency Path. Data Sovereignty traffic should flow in the direction of **xrd07** -> **xrd04** -> **xrd05** -> **xrd01**. We'll skip running the Data Sovereignty service on Rome and will do so later on the Amsterdam VM.
 
For reference if you wanted to run it on Rome:
```
./cleanup_rome_routes.sh 
python3 jalapeno.py -f rome.json -e srv6 -s ds
ping 10.101.2.1 -I 20.0.0.1 -i .3
```

## Amsterdam VM
### POC host-based SRv6 and SR-MPLS SDN using the VPP dataplane
In our lab the Amsterdam VM represents a content server whose application owners wish to provide optimal user experience, while balancing out the need for bulk content replication.  They've chosen to use VPP as their host-based SR/SRv6 forwarding engine, and have subscribed to the network services made available by our Jalapeno system.

Like the Rome VM, Amsterdam has the same `jalapeno.py` App that can query Jalapeno for SR/SRv6 path data, and then program its local VPP dataplane with ip route with SR/SRv6 encapsulation.

1. Login to the Amsterdam VM
```
ssh cisco@198.18.128.102
```

2. cd into the lab_6/python/ directory:
```
cd ~/SRv6_dCloud_Lab/lab_6/python/
```
2. Everything is the same as on the Rome VM with some different parameters in amsterdam.json:
```
cat ./amsterdam.json
```
3. Amsterdam has a Linux veth pair connecting kernel forwarding to its onboard VPP instance. The VM has preconfigured ip routes (see /etc/netplan/00-installer-config.yaml) pointing to VPP via its "ams-out" interface:
```
ip link | grep ams-out
ip route
```
Output:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_6$ ip link | grep ams-out
4: vpp-in@ams-out: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
5: ams-out@vpp-in: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000

cisco@amsterdam:~/SRv6_dCloud_Lab/lab_6$ ip route
default via 198.18.128.1 dev ens160 proto static 
default via 198.18.128.1 dev ens160 proto static metric 100 
10.0.0.0/24 via 10.101.2.2 dev ams-out proto static 
10.101.1.0/24 via 10.101.2.2 dev ams-out proto static 
10.101.2.0/24 dev ams-out proto kernel scope link src 10.101.2.1 
10.101.3.0/24 dev ens224 proto kernel scope link src 10.101.3.1 
10.107.0.0/20 via 10.101.2.2 dev ams-out proto static 
20.0.0.0/24 via 10.101.2.2 dev ams-out proto static 
30.0.0.0/24 via 10.101.2.2 dev ams-out proto static 
40.0.0.0/24 via 10.101.3.2 dev ens224 proto static 
50.0.0.0/24 via 10.101.3.2 dev ens224 proto static 
198.18.128.0/18 dev ens160 proto kernel scope link src 198.18.128.102 
```
4. VPP has been given a startup config which establishes IP connectivity to the network as a whole on bootup.
```
cat /etc/vpp/startup.conf
```
 - Note the 'unix' and 'dpdk' sections of the config:
```
unix {
  nodaemon
  log /var/log/vpp/vpp.log
  full-coredump
  cli-listen /run/vpp/cli.sock
  gid vpp
  startup-config /home/cisco/SRv6_dCloud_Lab/lab_1/config/vpp.conf
}
dpdk {
  dev 0000:0b:00.0
}
```
 - VPP startup-config file: https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_1/config/vpp.conf

1. VPP's CLI may be invoked directly:
```
sudo vppctl
```
```
show interface address
```
Example:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_6/python$ sudo vppctl
    _______    _        _   _____  ___ 
 __/ __/ _ \  (_)__    | | / / _ \/ _ \
 _/ _// // / / / _ \   | |/ / ___/ ___/
 /_/ /____(_)_/\___/   |___/_/  /_/    

vpp# show interface address
GigabitEthernetb/0/0 (up):
  L3 10.101.1.1/24
  L3 fc00:0:101:1::1/64
host-vpp-in (up):
  L3 10.101.2.2/24
local0 (dn):
vpp#  
vpp# quit
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_6/python$
```
6. VPP CLI can also be driven from the Linux command line:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_6$ sudo vppctl show interface address
GigabitEthernetb/0/0 (up):
  L3 10.101.1.1/24
  L3 fc00:0:101:1::1/64
host-vpp-in (up):
  L3 10.101.2.2/24
local0 (dn):
```
7. Other handy VPP commands:
```
quit                     # exit VPP CLI
show ip fib              # show VPP's forwarding table, which will include SR and SRv6 policy/encap info later
sudo vppctl show ip fib  # same command but executed from Linux
show interface           # interface status and stats
sudo vppctl show interface # same command but executed from Linux
```

### jalapeno.py on Amsterdam:
`jalapeno.py` operates on Amsterdam the same way it operates on the Rome VM, and it supports the same set of network services. *`amsterdam.json`* specifies to the use of a *`VPP`* dataplane, therefore the `jalapeno.py` will construct a VPP SRv6 route/policy upon completing its path calculation.

## Amsterdam Network Services
### Get All Paths

Examples for running the Get All Paths, Least Utilized, and Low Latency services on Amsterdam VM

1. Amsterdam 'get all paths':
``` 
python3 jalapeno.py -f amsterdam.json -e srv6 -s gp
```
 - Expected console output:

```
Get All Paths Service
number of paths found:  4

path locator list:  ['fc00:0:1111::', 'fc00:0:2222::', 'fc00:0:6666::', 'fc00:0:7777::']
srv6 sid for this path:  fc00:0:1111:2222:6666:7777::

path locator list:  ['fc00:0:1111::', 'fc00:0:5555::', 'fc00:0:4444::', 'fc00:0:7777::']
srv6 sid for this path:  fc00:0:1111:5555:4444:7777::

path locator list:  ['fc00:0:1111::', 'fc00:0:5555::', 'fc00:0:6666::', 'fc00:0:7777::']
srv6 sid for this path:  fc00:0:1111:5555:6666:7777::

path locator list:  ['fc00:0:1111::', 'fc00:0:2222::', 'fc00:0:3333::', 'fc00:0:4444::', 'fc00:0:7777::']
srv6 sid for this path:  fc00:0:1111:2222:3333:4444:7777::

All paths data from unicast_prefix_v4/10.101.2.0_24_10.0.0.1 to unicast_prefix_v4/20.0.0.0_24_10.0.0.7 logged to log/get_paths.json
```

### Least Utilized Path
The Least Utilized Path service behaves the same on Amsterdam as on Rome, except that it will program VPP forwarding. If encapsulation-type *`sr`* is chosen, the service simply programs VPP with a labeled IP route entry. If encap *`srv6`* is chosen the service will program VPP with a Binding-SID and SR-Policy. 

Once the "LU" path service is executed Amsterdam will be able to steer content replication traffic away from the best path and onto the least utilized path, thus preserving the routing protocol's best path for streaming video.

Note: `jalapeno.py` automatically cleans up old VPP routes/SR-policies prior to installing new ones:

1. Execute the least utilized path service with SRv6 encapsulation
``` 
python3 jalapeno.py -f amsterdam.json -e srv6 -s lu
```
 - The client's command line output will include info on VPP's new forwarding table:
```
cisco@amsterdam:~/SRv6_dCloud_Lab/lab_6/python$ python3 jalapeno.py -f amsterdam.json -e srv6 -s lu

Least Utilized Service
locator list for least utilized path:  ['fc00:0:2222::', 'fc00:0:3333::', 'fc00:0:4444::', 'fc00:0:7777::']
egress node locator:  fc00:0:7777::
end.dt SID:  ['fc00:0:7777:e007::']
srv6 sid:  fc00:0:2222:3333:4444:7777:e007::

adding vpp sr-policy to:  20.0.0.0/24 , with SRv6 encap:  fc00:0:2222:3333:4444:7777:e007::
sr steer: The requested SR steering policy could not be deleted.
sr policy: BUG: sr policy returns -1

Display VPP FIB entry: 
ipv4-VRF:0, fib_index:0, flow hash:[src dst sport dport proto flowlabel ] epoch:0 flags:none locks:[adjacency:1, default-route:1, ]
20.0.0.0/24 fib:0 index:36 locks:2
  SR refs:1 entry-flags:uRPF-exempt, src-flags:added,contributing,active,
    path-list:[41] locks:2 flags:shared, uPRF-list:39 len:0 itfs:[]
      path:[49] pl-index:41 ip6 weight=1 pref=0 recursive:  oper-flags:resolved,
        via 101::101 in fib:3 via-fib:35 via-dpo:[dpo-load-balance:37]

 forwarding:   unicast-ip4-chain
  [@0]: dpo-load-balance: [proto:ip4 index:38 buckets:1 uRPF:38 to:[0:0]]
    [0] [@14]: dpo-load-balance: [proto:ip4 index:37 buckets:1 uRPF:-1 to:[0:0]]
          [0] [@13]: SR: Segment List index:[0]
	Segments:< fc00:0:2222:3333:4444:7777:e007:0 > - Weight: 1      <------------ SRv6 Micro-SID encapsulation
```

1. You can also check the VPP FIB entry from linux:
 ```
sudo vppctl show ip fib 20.0.0.0/24
```

2. Run a ping test 
 - ssh to the **XRd VM** and start a tcpdump on the interface facing the Amsterdam VM:
```
ssh cisco@198.18.128.100
```
```
sudo tcpdump -lni ens224
```
 - Return to your Amsterdam ssh session and ping
```
ping 20.0.0.1 -i .4
```

3. Validate outbound traffic is encapsulated in the SRv6 label stack. Expected output will be something like:
```
cisco@xrd:~/SRv6_dCloud_Lab/util$ sudo tcpdump -lni ens224
<snip>
01:17:48.874686 IP6 fc00:0:101:1::1 > fc00:0:2222:3333:4444:7777:e007:0: IP 10.101.2.1 > 20.0.0.1: ICMP echo request, id 12, seq 3, length 64
01:17:48.949955 IP 20.0.0.1 > 10.101.2.1: ICMP echo reply, id 12, seq 3, length 64
```

4. Optional: run the extended ./tcpdump-xrd01-02-03-04-07.sh script for the hops along the path:
```
./tcpdump-xrd01-02-03-04-07.sh
```

### Low Latency Path
The procedure on Amsterdam is the same as Least Utilized Path

1. Low latency SRv6 path on Amsterdam VM:
```
python3 jalapeno.py -f amsterdam.json -e srv6 -s ll
```

Example truncated output:
```
 forwarding:   unicast-ip4-chain
  [@0]: dpo-load-balance: [proto:ip4 index:38 buckets:1 uRPF:38 to:[0:0]]
    [0] [@14]: dpo-load-balance: [proto:ip4 index:36 buckets:1 uRPF:-1 to:[0:0]]
          [0] [@13]: SR: Segment List index:[0]
	Segments:< fc00:0:5555:6666:7777:e007:: > - Weight: 1
```

2. The Low latency path should be *`xrd01`* -> *`xrd05`* -> *`xrd06`* -> *`xrd07`* -> Rome. 
   
3. Optional run a ping from Amsterdam VM and the tcpdump script On XRD VM as follows. Your ping times should have dropped at least a few ms:

  Ping from Amsterdam
  ```
  ping 20.0.0.1 -i .4
  ```
  XRD VM extended tcpdump:
  ```
  ./tcpdump-xrd01-05-06-07.sh 
  ```

### Data Sovereignty Path 

The procedure on Amsterdam is the same as the previous two services. In *`amsterdam.json`* we've specified *`FRA`* as the country to avoid, so all results should avoid *`xrd06`*.
 
1. Data Sovereignty via SRv6 path from Amsterdam VM:
```
python3 jalapeno.py -f amsterdam.json -e srv6 -s ds
```
Example truncated output:
```
 forwarding:   unicast-ip4-chain
  [@0]: dpo-load-balance: [proto:ip4 index:38 buckets:1 uRPF:40 to:[0:0]]
    [0] [@14]: dpo-load-balance: [proto:ip4 index:37 buckets:1 uRPF:-1 to:[0:0]]
          [0] [@13]: SR: Segment List index:[0]
	Segments:< fc00:0:5555:4444:7777:e007:: > - Weight: 1
```
2. The Data Sovereignty path should be *`xrd01`* -> *`xrd05`* -> *`xrd04`* -> *`xrd07`* -> Rome. 
3. Optional: ping from Amsterdam and run the tcpdump script On XRD VM as follows

Amsterdam:
```
ping 20.0.0.1 -i .4
```

XRD VM extended tcpdump:
```
./tcpdump-xrd01-05-06-07.sh 
```

4. Optional: modify the amsterdam.json file and replace *`FRA`* with *`DEU`*, *`POL`*, *`BEL`*, etc., then re-run the script.

```
python3 jalapeno.py -f amsterdam.json -e srv6 -s ds
```
### You have reached the end of LTRSPG-2212, hooray!
