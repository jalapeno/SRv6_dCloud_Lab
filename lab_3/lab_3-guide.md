# Lab 3: Configure SRv6 L3VPN and SRv6-TE [30 Min]

### Description
In Lab 3 we will establish a Layer-3 VPN named "carrots" which will use SRv6 transport and will have endpoints on **xrd01** and **xrd07**. In order to extend L3VPN "carrots" to the Amsterdam and Rome VM we will be adding the VRF "carrot" to interfaces on **xrd01** and **xrd07** that connect to seconrday NICs on the Amsterdam and Rome. Once the L3VPN is established and you run test traffic between Amsterdam and Rome we will then setup SRv6-TE traffic steering from Amsterdam to specific Rome prefixes.

## Contents
- [Lab 3: Configure SRv6 L3VPN and SRv6-TE \[30 Min\]](#lab-3-configure-srv6-l3vpn-and-srv6-te-30-min)
    - [Description](#description)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [Configure SRv6 L3VPN](#configure-srv6-l3vpn)
    - [Configure VRF](#configure-vrf)
    - [Add VRF to router interfaces for L3VPN](#add-vrf-to-router-interfaces-for-l3vpn)
    - [Configure BGP L3VPN Peering](#configure-bgp-l3vpn-peering)
  - [Validate SRv6 L3VPN](#validate-srv6-l3vpn)
  - [Configure SRv6-TE steering for L3VPN](#configure-srv6-te-steering-for-l3vpn)
    - [Create SRv6-TE steering policy](#create-srv6-te-steering-policy)
    - [Validate SRv6-TE steering of L3VPN traffic](#validate-srv6-te-steering-of-l3vpn-traffic)
      - [Validate bulk traffic takes the non-shortest path: xrd01 -\> 02 -\> 03 -\> 04 -\> 07](#validate-bulk-traffic-takes-the-non-shortest-path-xrd01---02---03---04---07)
      - [Validate low latency traffic takes the path: xrd01 -\> 05 -\> 06 -\> 07](#validate-low-latency-traffic-takes-the-path-xrd01---05---06---07)
    - [End of Lab 3](#end-of-lab-3)

## Lab Objectives
The student upon completion of Lab 3 should have achieved the following objectives:

* Understanding of SRv6 L3VPN
* Configuration of SRv6 L3VPN in XR
* Configuration of SRv6 TE policy
* Demonstartion of SRv6 TE traffic steering

## Configure SRv6 L3VPN
The SRv6-based IPv4/IPv6 L3VPN featureset enables operation of IPv4/IPv6 L3VPN over a SRv6 data plane. Traditionally L3VPN has been operated over MPLS or SR-MPLS based systems. SRv6 L3VPN uses the locator/function aspect of SRv6 Segment IDs (SIDs) instead of PE + VPN labels. 

Example: 

|     Locator    | Function |                                         
|:---------------|:--------:|
| fc00:0000:7777:|   e004:: |


SRv6 L3VPN functionality interconnects multiple sites to resemble a private network service over public or multi-tenant infrastructure. The basic SRv6 configuration was completed in [Lab 2](/lab_2/lab_2-guide.md).

In this lab a BGP SID will be allocated in per-VRF mode and provides End.DT4 or End.DT6 functionality. End.DT4/6 represents the Endpoint with decapsulation and IPv4 or v6 lookup in a specific VRF table.

For more details on SRv6 network programming Endpoint Behavior functionality please see RFC 8986 [LINK](https://datatracker.ietf.org/doc/html/rfc8986#name-enddt6-decapsulation-and-sp)

BGP encodes the SRv6 SID in the prefix-SID attribute of the IPv4/6 L3VPN Network Layer Reachability Information (NLRI) and advertises it to IPv6 peering over an SRv6 network. The Ingress PE (provider edge) router encapsulates the VRF IPv4/6 traffic with the SRv6 VPN SID and sends it over the SRv6 network.


  ### Configure VRF
  This lab will use the VRF *carrots* for IPv4 and IPv6 VPN. The *carrots* VRF is configured only on the two edge routers in our SP network: **xrd01** and **xrd07**. Intermediate routers do not need to be VRF aware and are instead forwarding on the SRv6 data plane.

  Configure the VRF on **xrd01** and **xrd07**:

  ```
  conf t
  vrf carrots
    address-family ipv4 unicast
      import route-target
      9:9
      export route-target
      9:9
    
    address-family ipv6 unicast
      import route-target
      9:9
      export route-target
      9:9

    commit
  ```

  ### Add VRF to router interfaces for L3VPN
  Now that our VRF *carrots* has been created lets get the VRF added to the applicable interfaces. For **xrd01** we will use  interface *GigabitEthernet0/0/0/3* which connects to Amsterdam over link *M*. For **xrd07** we will use interface *GigabitEthernet0/0/0/3* which connects to Rome over link *K*.

![iPerf Test](/topo_drawings/iperf-l3vpn.png)

 1. Add VRF to interfaces

    **xrd01**
    ```
    interface GigabitEthernet0/0/0/3
      vrf carrots
      ipv4 address 10.101.3.2 255.255.255.0
      ipv6 address fc00:0:101:3::2/64
      no shutdown
    commit
    ```

    **xrd07**  
    ```
    interface GigabitEthernet0/0/0/3
      vrf carrots
      ipv4 address 10.107.2.2 255.255.255.0
      ipv6 address fc00:0:107:2::2/64
      no shutdown
    commit
    ```


 2. Add VRF static routes  
     In addition to configuring *GigabitEthernet0/0/0/3* to be a member of VRF carrots, **xrd07** will need a pair of static routes for reachability to **Rome's** "40" and "50" network prefixes. Later we'll create SRv6-TE steering policies for traffic to the "40" and "50" prefixes:  

    **xrd07**
    ```
    router static
      vrf carrots
        address-family ipv4 unicast
          40.0.0.0/24 10.107.2.1
          50.0.0.0/24 10.107.2.1
        address-family ipv6 unicast
          fc00:0:40::/64 fc00:0:107:2::1
          fc00:0:50::/64 fc00:0:107:2::1
        commit
    ```

3. Verify **Rome** VRF prefix reachability  
    Ping check from xrd07 gi 0/0/0/3 to Rome VM via 2nd NIC:  
    ```
    ping vrf carrots 10.107.2.1
    ping vrf carrots 40.0.0.1
    ping vrf carrots 50.0.0.1
    ping vrf carrots fc00:0:107:2::1
    ping vrf carrots fc00:0:40::1
    ping vrf carrots fc00:0:50::1
    ```

4. Verify **Amsterdam** VRF prefix reachability  
    Ping check from **xrd01** gi 0/0/0/3 to **Amsterdam **VM via 2nd NIC:  
    ```
    ping vrf carrots 10.101.3.1
    ping vrf carrots fc00:0:101:3::1
    ```

### Configure BGP L3VPN Peering
The next step is to add the L3VPN configuration into BGP. The *carrots* L3VPN is dual-stack so we will be adding both vpnv4 and vpnv6 address-families to the BGP neighbor-group for ipv6 peers. For example you will enable L3VPN in the neighbor-group template by issuing the *address-family vpnv4/6 unicast* command.
  
 1. Enable BGP L3VPN 

    **xrd01** and **xrd07**
    ```
    conf t
    router bgp 65000
      neighbor-group xrd-ipv6-peer
        address-family vpnv4 unicast
        next-hop-self

        address-family vpnv6 unicast
        next-hop-self
      commit
    ```
  Next we add VRF *carrots* in BGP and enable SRv6 to each address family with the command *`segment-routing srv6`*. In addition we will tie the VRF to the SRv6 locator *`MyLocator`*. 

  Last on xrd01 we will redistribute connected routes using the command *`redistribute connected`*. 
  
  On xrd07 we will need to redistribute both the connected and static routes to provide reachability to Rome and its additional prefixes. For xrd07 we will add both *`redistribute connected`* and *`redistribute static`*

 1. Enable SRv6 for VRF carrots and redistribute connected/static
   
    **xrd01**  
    ```
    conf t
    router bgp 65000
      vrf carrots
        rd auto
        address-family ipv4 unicast
          segment-routing srv6
          locator MyLocator
          alloc mode per-vrf
          redistribute connected
      
        address-family ipv6 unicast
          segment-routing srv6
          locator MyLocator
          alloc mode per-vrf
          redistribute connected
        commit
    ```

    **xrd07**  
    ```
    conf t
    router bgp 65000
      vrf carrots
        rd auto
        address-family ipv4 unicast
          segment-routing srv6
          locator MyLocator
          alloc mode per-vrf
          redistribute static
          redistribute connected
      
        address-family ipv6 unicast
          segment-routing srv6
          locator MyLocator
          alloc mode per-vrf
          redistribute static
          redistribute connected
        commit
      ```

The BGP route reflectors will also need to have L3VPN capability added to their peering group.

3. BGP Route Reflectors **xrd05**, **xrd06**  
    ```
    conf t
    router bgp 65000
    neighbor-group xrd-ipv6-peer
      address-family vpnv4 unicast
      route-reflector-client
      
      address-family vpnv6 unicast
      route-reflector-client
    commit
    ```

## Validate SRv6 L3VPN

Validation command output examples can be found at this [LINK](https://github.com/jalapeno/SRv6_dCloud_Lab/blob/main/lab_3/validation-cmd-output.md)

1. From **xrd01** run the following set of validation commands (for the sake of time you can paste them in as a group, or spot check some subset of commands):

  ```
  show segment-routing srv6 sid
  show bgp vpnv4 unicast
  show bgp vpnv4 unicast rd 10.0.0.7:0 40.0.0.0/24
  show bgp vpnv6 unicast
  show bgp vpnv6 unicast rd 10.0.0.7:0 fc00:0:40::/64 
  ping vrf carrots 40.0.0.1
  ping vrf carrots 50.0.0.1
  ping vrf carrots fc00:0:40::1
  ping vrf carrots fc00:0:50::1
  ```

  Example validation for vpnv4 route
  ```
  RP/0/RP0/CPU0:xrd01#show bgp vpnv4 unicast rd 10.0.0.7:0 40.0.0.0/24   
  Tue Jan 31 23:36:41.390 UTC
  BGP routing table entry for 40.0.0.0/24, Route Distinguisher: 10.0.0.7:0   <--- WE HAVE A ROUTE. YAH
  Versions:
    Process           bRIB/RIB  SendTblVer
    Speaker                  11           11
    Last Modified: Jan 31 23:34:44.948 for 00:01:56
    Paths: (2 available, best #1)
      Not advertised to any peer
    Path #1: Received by speaker 0
    Not advertised to any peer
    Local
      fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)   <--------- SOURCE XRD07
        Received Label 0xe0040
        Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, not-in-vrf
        Received Path ID 0, Local Path ID 1, version 5
        Extended community: RT:9:9 
        Originator: 10.0.0.7, Cluster list: 10.0.0.5             <------- FROM RR XRD05
        PSID-Type:L3, SubTLV Count:1
        SubTLV:
          T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1
          SubSubTLV:
            T:1(Sid structure):
    Path #2: Received by speaker 0
    Not advertised to any peer
    Local
      fc00:0:7777::1 (metric 3) from fc00:0:6666::1 (10.0.0.7)
        Received Label 0xe0040
        Origin incomplete, metric 0, localpref 100, valid, internal, import-candidate, not-in-vrf
        Received Path ID 0, Local Path ID 0, version 0
        Extended community: RT:9:9 
        Originator: 10.0.0.7, Cluster list: 10.0.0.6             <------- FROM RR XRD06
        PSID-Type:L3, SubTLV Count:1
        SubTLV:
          T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1
          SubSubTLV:
            T:1(Sid structure):
  ```

## Configure SRv6-TE steering for L3VPN
**Rome's** L3VPN IPv4 and IPv6 prefixes are associated with two classes of traffic:

* The **"40"** destinations (40.0.0.0/24 and fc00:0:40::/64) are Bulk Transport destinations (content replication or data backups) and thus are latency and loss tolerant. 
  
* The **"50"** destinations (50.0.0.0/24 and fc00:0:50::/64) are for real time traffic (live video, etc.) and thus require the lowest latency path available.

We will use the below diagram for reference:

![L3VPN Topology](/topo_drawings/l3vpn-topology-large.png)

### Create SRv6-TE steering policy
For our SRv6-TE purposes we'll leverage the on-demand nexthop (ODN) feature set. Here is a nice example and explanation of ODN: [HERE](https://xrdocs.io/design/blogs/latest-converged-sdn-transport-ig)

Using the ODN method, our the egress PE, **xrd07**, will advertise its L3VPN routes with color extended communities. We'll do this by first defining the extcomms, then setting up route-policies to match on destination prefixes and set the extcomm values.

The ingress PE, **xrd01**, will then be configured with SRv6 segment-lists and SRv6 ODN steering policies that match routes with the respective color and apply the appropriate SID stack on outbound traffic.

1. On **xrd07** advertise Rome's "40" and "50" prefixes with their respective color extended communities:

  **xrd07**
  ```
  conf t
  extcommunity-set opaque bulk-transfer
    40
  end-set

  extcommunity-set opaque low-latency
    50
  end-set

  route-policy set-color
    if destination in (40.0.0.0/24) then
      set extcommunity color bulk-transfer
    endif
    if destination in (50.0.0.0/24) then
      set extcommunity color low-latency
    endif
    if destination in (fc00:0:40::/64) then
      set extcommunity color bulk-transfer
    endif
    if destination in (fc00:0:50::/64) then
      set extcommunity color low-latency
    endif
    pass
  end-policy

  router bgp 65000
  neighbor-group xrd-ipv6-peer
    address-family vpnv4 unicast
    route-policy set-color out
    
    address-family vpnv6 unicast
    route-policy set-color out
  commit
  ```

2. Validate vpnv4 and v6 prefixes are received at **xrd01** and that they have their color extcomms:  

  **xrd01**
  ```
  show bgp vpnv4 uni vrf carrots 40.0.0.0/24 
  show bgp vpnv4 uni vrf carrots 50.0.0.0/24
  show bgp vpnv6 uni vrf carrots fc00:0:40::/64
  show bgp vpnv6 uni vrf carrots fc00:0:50::/64
  ```
  - For easier reading you can filter the show command output:
  ```
  show bgp vpnv4 uni vrf carrots 40.0.0.0/24 | include *olor 
  ```

  Examples:
  ```
  RP/0/RP0/CPU0:xrd01#show bgp vpnv4 uni vrf carrots 40.0.0.0/24
  Sat Jan  7 21:27:26.645 UTC
  BGP routing table entry for 40.0.0.0/24, Route Distinguisher: 10.0.0.1:0
  Versions:
    Process           bRIB/RIB  SendTblVer
    Speaker                  58           58
  Last Modified: Jan  7 21:27:19.204 for 00:00:07
  Paths: (1 available, best #1)
    Not advertised to any peer
    Path #1: Received by speaker 0
    Not advertised to any peer
    Local
      fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
        Received Label 0xe0040
        Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, imported
        Received Path ID 0, Local Path ID 1, version 30
        Extended community: Color:40 RT:9:9                      <------------------- HERE
        Originator: 10.0.0.7, Cluster list: 10.0.0.5
        PSID-Type:L3, SubTLV Count:1
        SubTLV:
          T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1
          SubSubTLV:
            T:1(Sid structure):
        Source AFI: VPNv4 Unicast, Source VRF: default, Source Route Distinguisher: 10.0.0.7:0

  RP/0/RP0/CPU0:xrd01#show bgp vpnv6 uni vrf carrots fc00:0:50::/64
  Sat Jan  7 21:27:56.050 UTC
  BGP routing table entry for fc00:0:50::/64, Route Distinguisher: 10.0.0.1:0
  Versions:
    Process           bRIB/RIB  SendTblVer
    Speaker                  46           46
  Last Modified: Jan  7 21:27:19.204 for 00:00:36
  Paths: (1 available, best #1)
    Not advertised to any peer
    Path #1: Received by speaker 0
    Not advertised to any peer
    Local
      fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
        Received Label 0xe0050
        Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, imported
        Received Path ID 0, Local Path ID 1, version 34
        Extended community: Color:50 RT:9:9                      <------------------- HERE
        Originator: 10.0.0.7, Cluster list: 10.0.0.5
        PSID-Type:L3, SubTLV Count:1
        SubTLV:
          T:1(Sid information), Sid:fc00:0:7777::, Behavior:62, SS-TLV Count:1
          SubSubTLV:
            T:1(Sid structure):
        Source AFI: VPNv6 Unicast, Source VRF: default, Source Route Distinguisher: 10.0.0.7:0
  ```

1. On **xrd01** configure a pair of SRv6-TE segment lists for steering traffic over these specific paths through the network: 
    - Segment list *xrd2347* will execute the explicit path: xrd01 -> 02 -> 03 -> 04 -> 07
    - Segment list *xrd567* will execute the explicit path: xrd01 -> 05 -> 06 -> 07

  ![L3VPN Topology](/topo_drawings/l3vpn-slow-fast-path.png)

   **xrd01**
   ```
   conf t
   segment-routing
    traffic-eng
     segment-lists
      srv6
       sid-format usid-f3216
      
      segment-list xrd2347
       srv6
        index 10 sid fc00:0:2222::
        index 20 sid fc00:0:3333::
        index 30 sid fc00:0:4444::

      segment-list xrd567
       srv6
        index 10 sid fc00:0:5555::
        index 20 sid fc00:0:6666::
     commit
   ```

4. On **xrd01** configure our bulk transport and low latency SRv6 steering policies. Low latency traffic will be forced over the *xrd01-05-06-07* path, and bulk transport traffic will take the longer *xrd01-02-03-04-07* path:

  **xrd01**
  ```
  conf t
  segment-routing
  traffic-eng
    policy bulk-transfer
    srv6
      locator MyLocator binding-sid dynamic behavior ub6-insert-reduced
    
    color 40 end-point ipv6 fc00:0:7777::1
    candidate-paths
      preference 100
      explicit segment-list xrd2347
      
    policy low-latency
    srv6
      locator MyLocator binding-sid dynamic behavior ub6-insert-reduced
    
    color 50 end-point ipv6 fc00:0:7777::1
    candidate-paths
      preference 100
      explicit segment-list xrd567
    commit
  ```

5. Validate **xrd01's** SRv6-TE SID is allocated and that policy is up:
  ```
  show segment-routing srv6 sid
  show segment-routing traffic-eng policy 
  ```
  Example output, note the additional uDT VRF carrots and SRv6-TE **uB6 Insert.Red** SIDs added to the list:
  ```
  RP/0/RP0/CPU0:xrd01#  show segment-routing srv6 sid
  Sat Dec 16 02:45:31.772 UTC

  *** Locator: 'MyLocator' *** 

  SID                         Behavior          Context                           Owner               State  RW
  --------------------------  ----------------  --------------------------------  ------------------  -----  --
  fc00:0:1111::               uN (PSP/USD)      'default':4369                    sidmgr              InUse  Y 
  fc00:0:1111:e000::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
  fc00:0:1111:e001::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
  fc00:0:1111:e002::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
  fc00:0:1111:e003::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
  fc00:0:1111:e004::          uDT6              'default'                         bgp-65000           InUse  Y 
  fc00:0:1111:e005::          uDT4              'default'                         bgp-65000           InUse  Y 
  fc00:0:1111:e006::          uB6 (Insert.Red)  'srte_c_50_ep_fc00:0:7777::1' (50, fc00:0:7777::1)  xtc_srv6            InUse  Y 
  fc00:0:1111:e007::          uB6 (Insert.Red)  'srte_c_40_ep_fc00:0:7777::1' (40, fc00:0:7777::1)  xtc_srv6            InUse  Y 
  fc00:0:1111:e008::          uDT4              'carrots'                         bgp-65000           InUse  Y 
  fc00:0:1111:e009::          uDT6              'carrots'                         bgp-65000           InUse  Y 


  RP/0/RP0/CPU0:xrd01#show segment-routing traffic-eng policy 
  Sat Jan 28 00:06:23.479 UTC

  SR-TE policy database
  ---------------------

  Color: 50, End-point: fc00:0:7777::1
    Name: srte_c_50_ep_fc00:0:7777::1
    Status:
      Admin: up  Operational: up for 00:23:59 (since Jan 27 23:42:24.041)
    Candidate-paths:
      Preference: 100 (configuration) (active)
        Name: low-latency
        Requested BSID: dynamic
        Constraints:
          Protection Type: protected-preferred
          Maximum SID Depth: 19 
        Explicit: segment-list xrd567 (valid)      <------------- HERE
          Weight: 1, Metric Type: TE
            SID[0]: fc00:0:5555::/48
                    Format: f3216
                    LBL:32 LNL:16 FL:0 AL:80
            SID[1]: fc00:0:6666::/48
                    Format: f3216
                    LBL:32 LNL:16 FL:0 AL:80
        SRv6 Information:
          Locator: MyLocator
          Binding SID requested: Dynamic
          Binding SID behavior: End.B6.Insert.Red
    Attributes:
      Binding SID: fc00:0:1111:e006::
      Forward Class: Not Configured
      Steering labeled-services disabled: no
      Steering BGP disabled: no
      IPv6 caps enable: yes
      Invalidation drop enabled: no
      Max Install Standby Candidate Paths: 0
  ```

### Validate SRv6-TE steering of L3VPN traffic
#### Validate bulk traffic takes the non-shortest path: xrd01 -> 02 -> 03 -> 04 -> 07 
1. Run the tcpdump.sh script in the XRD VM's util directory on the following links in the network. These can either be run sequentially while executing the ping in step 2, or you can open individual ssh sessions and run the tcpdumps simultaneously. 
 
As you run the tcpdumps you should see SRv6 Micro-SID 'shift-and-forward' behavior in action. Feel free to run all, or just one or two tcpdumps. Alternatively you can run **./tcpdump-xrd01-02-03-04-07.sh** which will tcpdump for a few seconds along each link in the path.
  
    ```
    cd SRv6_dCloud_Lab/util/

    ./tcpdump.sh xrd01-xrd02
    ```
    ```
    ./tcpdump.sh xrd02-xrd03
    ```
    ```
    ./tcpdump.sh xrd03-xrd04
    ```
    ```
    ./tcpdump.sh xrd04-xrd07
    ```

3. Ping from Amsterdam to Rome's bulk transport destination IPv4 and IPv6 addresses:

    ```
    ping 40.0.0.1 -i .4
    ```
    ```
    ping fc00:0:40::1 -i .4
    ```

    Example: tcpdump.sh output should look something like below on the **xrd02-xrd03** link with both outer SRv6 uSID header and inner IPv4/6 headers. In this case the outbound traffic is taking a non-shortest path.  We don't have a specific policy for return traffic so it will take one of the ECMP shortest paths; thus we do not see replies in the tcpdump output:
    ```
    IPv4 payload:

    18:43:55.837052 IP6 fc00:0:1111::1 > fc00:0:3333:4444:7777:e004::: IP 10.101.3.1 > 40.0.0.1: ICMP echo request, id 2, seq 1, length 64
    18:43:56.238255 IP6 fc00:0:1111::1 > fc00:0:3333:4444:7777:e004::: IP 10.101.3.1 > 40.0.0.1: ICMP echo request, id 2, seq 2, length 64

    IPv6 payload:

    18:44:13.268208 IP6 fc00:0:1111::1 > fc00:0:3333:4444:7777:e005::: IP6 fc00:0:101:3:250:56ff:fe97:22cc > fc00:0:40::1: ICMP6, echo request, seq 1, length 64
    18:44:13.668766 IP6 fc00:0:1111::1 > fc00:0:3333:4444:7777:e005::: IP6 fc00:0:101:3:250:56ff:fe97:22cc > fc00:0:40::1: ICMP6, echo request, seq 2, length 64
    ```

    - Note: we have found an occasional issue where IPv6 neighbor discovery fails between *`Amsterdam`* Linux and the XRd MACVLAN attachment on *`xrd01`*. So if your IPv6 ping from *`Amsterdam`* doesn't work try pinging from *`xrd01`* to *`Amsterdam`* over the VRF carrots interface. A successful ping should 'wake up' the IPv6 neighborship.

    On *`xrd01`*:  
    ```
    ping vrf carrots fc00:0:101:3::1 
    ```
    Output:
    ```
    RP/0/RP0/CPU0:xrd01#ping vrf carrots fc00:0:101:3::1 
    Thu Feb  2 16:33:42.984 UTC
    Type escape sequence to abort.
    Sending 5, 100-byte ICMP Echos to fc00:0:101:3::1, timeout is 2 seconds:
    !!!!!
    Success rate is 100 percent (5/5), round-trip min/avg/max = 3/4/4 ms
    RP/0/RP0/CPU0:xrd01#
    ```

#### Validate low latency traffic takes the path: xrd01 -> 05 -> 06 -> 07 
1.  Ping from **Amsterdam** to **Rome's** low latency destination IPv4 and IPv6 addresses while running the tcpdump script:

    ```
    ping 50.0.0.1 -i .4
    ```
    ```
    ping fc00:0:50::1 -i .4
    ```

    Tcpdump along the low latency path (feel free to run one or more of the below, or run **./tcpdump-xrd01-05-06-07.sh** which will tcpdump for a few seconds along each link in the path.
    ```
    ./tcpdump.sh xrd01-xrd05
    ```
    ```
    ./tcpdump.sh xrd05-xrd06
    ```
    ```
    ./tcpdump.sh xrd06-xrd07
    ```

    Example: tcpdump.sh output should look something like below on the **xrd05-xrd06** link. In this case **xrd05 -> 06 -> 07** is one of the IGP shortest paths. In this test run the IPv4 ping replies are taking the same return path, however the IPv6 ping replies have been hashed onto one of the other ECMP paths. Your results may vary depending on how the XRd nodes have hashed their flows:
    
    ```
    18:47:20.342018 IP6 fc00:0:1111::1 > fc00:0:6666:7777:e004::: IP 10.101.3.1 > 50.0.0.1: ICMP echo request, id 4, seq 1, length 64
    18:47:20.742775 IP6 fc00:0:1111::1 > fc00:0:6666:7777:e004::: IP 10.101.3.1 > 50.0.0.1: ICMP echo request, id 4, seq 2, length 64

    18:48:18.593766 IP6 fc00:0:1111::1 > fc00:0:6666:7777:e005::: IP6 fc00:0:101:3:250:56ff:fe97:22cc > fc00:0:50::1: ICMP6, echo request, seq 1, length 64
    18:48:18.995022 IP6 fc00:0:1111::1 > fc00:0:6666:7777:e005::: IP6 fc00:0:101:3:250:56ff:fe97:22cc > fc00:0:50::1: ICMP6, echo request, seq 2, length 64

    ```
    If you don't see return traffic on the same path you can run tcpdump.sh on other interfaces in the network. Here we found the return traffic for the IPv6 ping:
    ```
    ./tcpdump.sh xrd04-xrd05
    ```
    ```
    cisco@xrd:~/SRv6_dCloud_Lab/util$ ./tcpdump.sh xrd04-xrd05
    sudo tcpdump -ni br-9c9433e006cf
    tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
    listening on br-9c9433e006cf, link-type EN10MB (Ethernet), capture size 262144 bytes
    18:48:55.216409 IP6 fc00:0:7777::1 > fc00:0:1111:e004::: IP6 fc00:0:50::1 > fc00:0:101:3:250:56ff:fe97:22cc: ICMP6, echo reply, seq 1, length 64
    18:48:55.625467 IP6 fc00:0:7777::1 > fc00:0:1111:e004::: IP6 fc00:0:50::1 > fc00:0:101:3:250:56ff:fe97:22cc: ICMP6, echo reply, seq 2, length 64
    ```

### End of Lab 3
Please proceed to [Lab 4](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_4/lab_4-guide.md)
