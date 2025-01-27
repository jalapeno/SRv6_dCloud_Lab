
# Lab 5 Part 2: Host-Based SRv6

The goals of the Jalapeno project are:

1. Enable applications to directly control their network experience by giving them the ability to apply SRv6 policies/encapsulations to their own traffic
   
2. Enable developers to quickly and easily build network control or SDN Apps that client applications may use achieve goal #1 
   
In Part 2 we will use the **srctl** command line tool to program SRv6 routes on the Amsterdam and Rome VMs, thus enabling the hosts or their workloads to the direct control that we've been discussing.

## Contents
- [Lab 5 Part 2: Host-Based SRv6](#lab-5-part-2-host-based-srv6)
  - [Contents](#contents)
  - [Host-Based SR/SRv6 and building your own SDN App](#host-based-srsrv6-and-building-your-own-sdn-app)
    - [Why host-based SRv6?](#why-host-based-srv6)
  - [Lab Objectives](#lab-objectives)
  - [srctl command line tool](#srctl-command-line-tool)
  - [Rome VM: SRv6 on Linux](#rome-vm-srv6-on-linux)
    - [Rome to Amsterdam: Lowest Latency Path](#rome-to-amsterdam-lowest-latency-path)
  - [Amsterdam VM: SRv6 on VPP](#amsterdam-vm-srv6-on-vpp)
    - [Amsterdam to Rome: Least Utilized Path](#amsterdam-to-rome-least-utilized-path)
  - [Berlin VM - not quite Cilium SRv6-TE](#berlin-vm---not-quite-cilium-srv6-te)
    - [Berlin to Rome: Data Sovereignty Path](#berlin-to-rome-data-sovereignty-path)
  - [Get All Paths](#get-all-paths)
  - [Low Latency Re-Route](#low-latency-re-route)
    - [You have reached the end of LTRSPG-2212, hooray!](#you-have-reached-the-end-of-ltrspg-2212-hooray)

## Host-Based SR/SRv6 and building your own SDN App

We won't claim to be professional developers, but using Jalapeno and just a few hours of python coding we were able to build an SRv6 SDN App called **"srctl"**. Our App can program SRv6-TE routes/policies on Linux hosts/VMs and on [VPP](https://fd.io/). 

**srctl** is still under development and is modeled after Kubernetes' *kubectl* command line tool. It gives a sense of the power and possibilities when combining *SRv6 and host-based or cloud-native networking*. 

And if the two of us knuckleheads can cobble together a functional SDN App in a couple of hours, imagine what a group of real developers could do in a few short weeks!

### Why host-based SRv6? 

* **Flexibility and Control**: We get tremendous control of the SRv6 SIDs and our encapsulation depth isn't subject to ASIC limitations

* **Performance and Massive Scale**: With host-based SRv6 traffic reaches the transport network already encapsulated, thus the ingress PE or SRv6-TE headend doesn't need all the resource intense policy configuration; they just statelessly forward traffic per the SRv6 encapsulation or Network Program
  
* **SRv6 as Common E2E Architecture**: We could extend SRv6 into the Cloud! Or to IoT devices or other endpoints connected to the physical network...
 
We feel this ability to perform SRv6 operations at the host or other endpoint is a game changer which opens up enormous potential for innovation!

## Lab Objectives
The student upon completion of Lab 6 should have achieved the following objectives:

* Understanding of the SRv6 stack available in Linux
* Understanding the use of VPP as a host-based SRv6 forwarding element 
* How to use the **srctl** command line tool to program SRv6 routes on Linux hosts or VPP

## srctl command line tool
As mentioned in the introduction, **srctl** is a command line tool that allows us to access SRv6 network services by programing SRv6 routes on Linux hosts or VPP. It is modeled after *kubectl*, and as such it expects to be fed a yaml file defining the source and destination prefixes for which we want a specific SRv6 network service. When the user runs the command, **srctl** will call the Jalapeno API and pass the list of source and destination prefixes and the requested network service(s) or constraint(s). Jalapeno will perform its path calculations and will return a set of SRv6 instructions. **srctl** will then program the SRv6 routes on the Linux host or VPP.

 `srctl's` currently supported network services are: 

 - Low Latency Path
 - Least Utilized Path
 - Data Sovereignty Path
 - Get All Paths (informational only)

## Rome VM: SRv6 on Linux

The Rome VM is simulating a user host or endpoint and will use its Linux dataplane to perform SRv6 traffic encapsulation:

 - Linux SRv6 route reference: https://segment-routing.org/index.php/Implementation/Configuration

   1.  Login to the Rome VM
   ```
   ssh cisco@198.18.128.103
   ```

2. Run *srctl --help* to see the help menu for the tool.
   ```
   srctl --help
   ```

   Expected output:
   ```yaml
   cisco@rome:~$ srctl --help
   Usage: srctl [OPTIONS] COMMAND [ARGS]...

     Command line interface for Segment Routing Configuration

   Options:
     --api-server TEXT  Jalapeno API server address
     --help             Show this message and exit.

   Commands:
     apply   Apply a configuration from file
     delete  Delete a configuration from file
   ```

   Per the *help* output we see that our current options are to *apply* or *delete* a configuration from a yaml file.

3. Here is a commented version of Rome's srctl yaml file:
   
   ```yaml
   apiVersion: jalapeno.srv6/v1     # following the k8s design pattern, the api version
   kind: PathRequest                # the type of object we are creating, a path request of Jalapeno
   metadata:
     name: rome-routes              # the name of the object
   spec:
     platform: linux             # we specify the platform so srctl knows which type of routes to install (linux or vpp)
     defaultVrf:                 # also supports linux and vpp VRFs or tables
       ipv4:                     # address family
         routes:                 # a list of routes for which we want SRv6 services
           - name: rome-to-amsterdam-v4           # the name of the route
             graph: ipv4_graph                    # the Jalapeno graph to use for calculating the route
             pathType: shortest_path              # the type of path to use for the route
             metric: utilization                  # the metric to use for the route
             source: hosts/rome                   # the source's database ID
             destination: hosts/amsterdam         # the destination's database ID
             destination_prefix: "10.101.2.0/24"  # the destination prefix
             outbound_interface: "ens192"         # the linux or VPP outbound interface
 
       ipv6:      # the same applies to ipv6
         routes:
           - name: rome-to-amsterdam-v6
             graph: ipv6_graph
             pathType: shortest_path
             metric: utilization
             source: hosts/rome
             destination: hosts/amsterdam
             destination_prefix: "fc00:0:101:2::/64"
             outbound_interface: "ens192"
   ```

   4. cd into the *lab_5/srctl* directory. If you like you can review the yaml files in the directory - they should basically match the commented example.

   ```
   cd ~/SRv6_dCloud_Lab/lab_5/srctl
   cat rome.yaml
   ```

   5. For SRv6 outbound encapsulation we'll need to set Rome's SRv6 source address:

   ```
   sudo ip sr tunsrc set fc00:0:107:1::1
   ```

### Rome to Amsterdam: Lowest Latency Path

Our first use case is to make path selection through the network based on the cummulative link latency from A to Z. Calculating best paths using latency meta-data is not something traditional routing protocols can do. It may be possible to statically build routes through your network using weights to define a path. However, what these workarounds cannot do is provide path selection based on near real time data which is possible with an application like Jalapeno. This provides customers to have a flexible network policy that can react to changes in the WAN environment.

1. From the *lab_5/srctl* directory on Rome, run the following command (note, we add *sudo* to the command as we are applying the routes to the Linux host):
   ```
   sudo srctl --api-server http://198.18.128.101:30800 apply -f rome.yaml
   ```

   The Output should look something like this:
   ```yaml
   cisco@rome:~/SRv6_dCloud_Lab/lab_5/srctl$ sudo srctl --api-server http://198.18.128.101:30800 apply -f rome.yaml
   Loaded configuration from rome.yaml
   Deleted existing route to 10.101.2.0/24 in table 0  # cleanup existing route
   Adding route with encap: {'type': 'seg6', 'mode': 'encap', 'segs': ['fc00:0:7777:6666:2222:1111:0:0']} to table 0  # add new route
   Adding route with encap: {'type': 'seg6', 'mode': 'encap', 'segs': ['fc00:0:7777:6666:2222:1111:0:0']} to table 0
   rome-to-amsterdam-v4: fc00:0:7777:6666:2222:1111: Route to 10.101.2.0/24 via fc00:0:7777:6666:2222:1111:0:0 programmed successfully in table 0  # success message
   rome-to-amsterdam-v6: fc00:0:7777:6666:2222:1111: Route to fc00:0:101:2::/64 via fc00:0:7777:6666:2222:1111:0:0 programmed successfully in table 0  # success message
   ```

2. Take a look at the Linux route table on Rome to see the new routes:
   ```
   ip route show 
   ip -6 route show 
   ```

   Expected truncated output for ipv4:
   ```
   10.101.2.0/24  encap seg6 mode encap segs 1 [ fc00:0:7777:6666:2222:1111:: ] dev ens192 proto static 
   ```

   Expected truncated output for ipv6:
   ```
   fc00:0:101:2::/64  encap seg6 mode encap segs 1 [ fc00:0:7777:6666:2222:1111:: ] dev ens192 proto static metric 1024 pref medium
   ```

3. Run a ping test from Rome to Amsterdam.
   ```
   ping fc00:0:101:1::1 -i .4
   ```

   Optional: run tcpdump on the XRD VM to see the traffic flow and SRv6 uSID in action. 
   ```
   sudo ip netns exec clab-cleu25-xrd07 tcpdump -lni Gi0-0-0-0
   sudo ip netns exec clab-cleu25-xrd06 tcpdump -lni Gi0-0-0-0
   ```

   We expect the ping to work, and tcpdump output should look something like this:
   ```yaml
   cisco@xrd:~$ sudo ip netns exec clab-cleu25-xrd06 tcpdump -lni Gi0-0-0-0
   tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
   listening on Gi0-0-0-0, link-type EN10MB (Ethernet), capture size 262144 bytes
   22:23:10.294176 IP6 fc00:0:107:1::1 > fc00:0:6666:2222:1111::: srcrt (len=2, type=4, segleft=0[|srcrt]
   22:23:10.301615 IP6 fc00:0:101:1::1 > fc00:0:7777::: IP6 fc00:0:101:2::1 >  fc00:0:107:1:250:56ff:fe97:11bb: ICMP6, echo reply, seq 1, length 64
   22:23:10.694957 IP6 fc00:0:107:1::1 > fc00:0:6666:2222:1111::: srcrt (len=2, type=4, segleft=0[|srcrt]
   22:23:10.701436 IP6 fc00:0:101:1::1 > fc00:0:7777::: IP6 fc00:0:101:2::1 > fc00:0:107:1:250:56ff:fe97:11bb: ICMP6, echo reply, seq 2, length 64
   ```

## Amsterdam VM: SRv6 on VPP

In our lab the Amsterdam VM represents a content server whose application owners wish to provide optimal user experience, while balancing out the need for bulk content replication.  They've chosen to use VPP as their host-based SR/SRv6 forwarding engine, and have subscribed to the network services made available by our Jalapeno system and accessible via the *srctl* command line tool.

1. Login to the Amsterdam VM
```
ssh cisco@198.18.128.102
```

1. Amsterdam has a Linux veth pair connecting kernel forwarding to its onboard VPP instance. The VM has preconfigured ip routes (see /etc/netplan/00-installer-config.yaml) pointing to VPP via its "ams-out" interface:
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

### Amsterdam to Rome: Least Utilized Path

Many segment routing and other SDN solutions focus on the *low latency path* as their primary use case. We absolutely feel low latency is an important network service, especially for real time applications. However, we believe one of the use cases which deliver the most bang for the buck is **Least Utilized Path**. The idea behind this use case is that the routing protocol's chosen best path is very often *`The Actual Best Path`*. Because of this `srctl's` *`Least Utilized`* service looks to steer lower priority traffic (backups, content replication, etc.) to lesser used paths and preserve the routing protocol's *"best path"* for higher priority traffic.

1. ssh to the Amsterdam VM and cd into the *lab_5/srctl* directory. 
   ```
   ssh cisco@198.18.128.102
   cd ~/SRv6_dCloud_Lab/lab_5/srctl
   ```

2. Here is a commented portion of Amsterdam's *srctl* yaml file. Note the platform is *vpp* and we need to specify a *binding SID* or *bsid* for VPP. Also note the *pathType* and *metric* comments indicating we still want the shortest path, but it should be based on the lowest avg utilization.
   
   ```yaml
   apiVersion: jalapeno.srv6/v1
   kind: PathRequest
   metadata:
     name: amsterdam-routes
   spec:
     platform: vpp    # srctl knows that it will be programming VPP routes (technically sr policies)
     defaultVrf:  
       ipv4:
         routes:
           - name: amsterdam-to-rome-v4
             graph: ipv4_graph
             pathType: shortest_path  # the path type is a signal to the API/DB to use the shortest path algorithm based on the specified metric
             metric: utilization   # in the case we're specifying shortest_path based on lowest avg utilization
             source: hosts/amsterdam
             destination: hosts/rome
             destination_prefix: "10.107.1.0/24"
             bsid: "101::101"                       # Required for VPP
   ```


3. Run **srctl** *Least Utilized* service on Amsterdam VM
   ```
   sudo srctl --api-server http://198.18.128.101:30800 apply -f amsterdam.yaml
   ```

   Expected output:
   ```yaml
   cisco@amsterdam:~/SRv6_dCloud_Lab/lab_5/srctl$ sudo srctl --api-server http://198.18.128.101:30800 apply -f amsterdam.yaml
   Loaded configuration from amsterdam.yaml
   amsterdam-to-rome-v4: fc00:0:1111:2222:3333:4444:7777: Route programmed successfully
   amsterdam-to-rome-v6: fc00:0:1111:2222:3333:4444:7777: Route programmed successfully
   ```

4. Check VPP's SR policies table. Note the assigned Binding SIDs and uSID structured segment lists.
   ```
   sudo vppctl show sr policies
   ```

   Expected output:
   ```yaml
   cisco@amsterdam:~/SRv6_dCloud_Lab/lab_5/srctl$ sudo vppctl show sr policies
   SR policies:
   [0].-	BSID: 101::102
     Behavior: Encapsulation
     Type: Default
     FIB table: 0
     Segment Lists:
       [0].- < fc00:0:1111:2222:3333:4444:7777:0 > weight: 1
   -----------
   [1].-	BSID: 101::101
     Behavior: Encapsulation
     Type: Default
     FIB table: 0
     Segment Lists:
       [1].- < fc00:0:1111:2222:3333:4444:7777:0 > weight: 1
   -----------
   ```

5. Check VPP's SR traffic steering rules. 
   ```
   sudo vppctl show sr steering-policies
   ```

   Expected output:
   ```yaml
   cisco@amsterdam:~/SRv6_dCloud_Lab/lab_5/srctl$ sudo vppctl show sr steering-policies
   SR steering policies:
   Traffic		SR policy BSID
   L3 10.107.1.0/24	101::101
   L3 fc00:0:107:1::/64	101::102
   ```

   Note the steering rules match on an ipv4 or ipv6 destination prefix and set the SR policy BSID. Traffic arriving at VPP's ingress destined for the prefixes listed in the steering rules will be steered to the Binding SID's SR policy 

   Optional: check the VPP FIB table to see the SRv6 policy programmed.
   ```
   sudo vppctl show ip6 fib fc00:0:107:1::/64
   ```

   Expected output:
   ```yaml
   cisco@amsterdam:~$ sudo vppctl show ip6 fib fc00:0:107:1::/64
   ipv6-VRF:0, fib_index:0, flow hash:[src dst sport dport proto flowlabel ] epoch:0 flags:none locks:[adjacency:1, default-route:1, ]
   fc00:0:107:1::/64 fib:0 index:40 locks:2
     SR refs:1 entry-flags:uRPF-exempt, src-flags:added,contributing,active,
       path-list:[48] locks:2 flags:shared, uPRF-list:42 len:0 itfs:[]
         path:[60] pl-index:48 ip6 weight=1 pref=0 recursive:  oper-flags:resolved,
           via 101::102 in fib:4 via-fib:37 via-dpo:[dpo-load-balance:39]             # via BSID 101::102

   forwarding:   unicast-ip6-chain
     [@0]: dpo-load-balance: [proto:ip6 index:42 buckets:1 uRPF:41 to:[18891:1964664]]
       [0] [@23]: dpo-load-balance: [proto:ip6 index:39 buckets:1 uRPF:-1 to:[0:0] via:[18891:1964664]]
             [0] [@22]: SR: Segment List index:[0]  # BSID recurses to sr policy encapsulation
     Segments:< fc00:0:1111:2222:3333:4444:7777:0 > - Weight: 1
   SRv6 steering of IP4 prefixes through BSIDs, fib_index:3, flow hash:[src dst sport dport proto flowlabel ] epoch:0 flags:none locks:[SR:1, recursive-resolution:1, ]
   ```

6. Run a ping test. From the Amsterdam VM, ping Rome:
   ```
   ping fc00:0:107:1::1 -i .4
   ```

   Optional: run tcpdump on the XRD VM to see the traffic flow and SRv6 uSID in action. 
   ```
   sudo ip netns exec clab-cleu25-xrd01 tcpdump -lni Gi0-0-0-0
   sudo ip netns exec clab-cleu25-xrd03 tcpdump -lni Gi0-0-0-0
   ```

   We expect the ping to work, and because the outbound traffic is taking the least utilized path, and the return traffic is taking the low latency path we expect the above tcpdump output to only show SRv6 encapsulated ping requests:
   ```yaml
   cisco@xrd:~$ sudo ip netns exec clab-cleu25-xrd03 tcpdump -lni Gi0-0-0-0
   tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
   listening on Gi0-0-0-0, link-type EN10MB (Ethernet), capture size 262144 bytes
   22:49:37.171693 IP6 fc00:0:101:1::1 > fc00:0:3333:4444:7777::: IP6 fc00:0:101:2::1 > fc00:0:107:1::1: ICMP6, echo request, seq 34, length 64
   22:49:37.571757 IP6 fc00:0:101:1::1 > fc00:0:3333:4444:7777::: IP6 fc00:0:101:2::1 > fc00:0:107:1::1: ICMP6, echo request, seq 35, length 64
   ```

  > [!NOTE]
  > If we wanted to implement either the Amsterdam or Rome or Rome to Amsterdam SRv6 service for global table traffic as an SRv6-TE steering policy on our xrd routers we would create a policy like the below example, which is very similar to the work we did in Lab 3 for L3VPN prefixes.
     
  On router **xrd07** we need to add in config to advertise the global prefix with the bulk transfer community.
     ```
     extcommunity-set opaque bulk-transfer
       40
     end-set

     route-policy set-global-color
        if destination in (fc00:0:107:1::/64) then
          set extcommunity color bulk-transfer
        endif
        pass
     end-policy 
     ```
  
  Then on router **xrd01** we would add an SRv6 segment-list config to define the hops returned from our query between router **xrd01** (source) and **xrd07** (destination). 
   
  ```
  segment-routing
  traffic-eng
    segment-lists
      segment-list xrd2347
        srv6
         index 10 sid fc00:0:2222::
         index 20 sid fc00:0:3333::
         index 30 sid fc00:0:4444:: 

    policy bulk-transfer
     srv6
      locator MyLocator binding-sid dynamic behavior ub6-insert-reduced
     !
     color 40 end-point ipv6 fc00:0:7777::1
     candidate-paths
      preference 100
       explicit segment-list xrd2347
  ```

## Berlin VM - not quite Cilium SRv6-TE
On the Berlin VM we have our K8s pods which are connected to Cilium SRv6 L3VPN instances. However, Cilium doesn't currently support SRv6-TE. But as we saw with Rome, Linux does! So for now we'll use **srctl** to program a Berlin to Rome path, but we'll specify Linux as the platform. Hopefully by this time next year Cilium will support SRv6-TE and we'll add it to the list of *srctl* platforms.

### Berlin to Rome: Data Sovereignty Path

The Data Sovereignty service enables the user or application to steer their traffic through a path or geography that is considered safe per a set of legal guidelines or other regulatory framework. In our case the *`dataSovereignty`* service allows us to choose a country (or countries) to avoid when transmitting traffic from a source to a given destination. The country to avoid is specified as a country code in the *srctl* yaml file. 

In our testing we've specified that traffic should avoid France (FRA) - no offense, its just the easiest path in our topology to demonstrate. *`xrd06`* is located in Paris, so all requests to the *`dataSovereignty`* service should produce a shortest-path result that avoids *`xrd06`*.



## Get All Paths

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




## Low Latency Re-Route
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



### You have reached the end of LTRSPG-2212, hooray!

