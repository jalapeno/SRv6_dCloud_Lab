# Lab 5: Install Jalapeno and enable BMP

### Description
In Lab 5 we will install the open-source Jalapeno data infrastructure platform. Jalapeno will leverage a Kubernetes environment that allows us to install not only Jalapeno but, the entire support software stack. Kubernetes experience is not required for Lab 5 as we have included the required validation commands. Next the student will then configure BGP Monitoring Protocol (BMP) on our route reflectors. Last we will add in support for SRv6 sourced traffic originating from Amsterdam and Rome.

## Contents
1. [Install Jalapeno](#install-jalapeno)
2. [Install Jalapeno SR-Processors](#install-jalapeno-sr-processors)
3. [BGP Monitoring Protocol](#bgp-monitoring-protocol-bmp)
4. [BGP SRv6 Locator](#configure-a-bgp-srv6-locator)

### Install Jalapeno 
Project Jalapeno combines existing open source tools with some new stuff we've developed into an infrastructure platform intended to enable development of "Cloud Native Network Services" (CNNS). Think of it as applying microservices architecture to SDN: give developers the ability to quickly and easily build microservice control planes (CNNS) on top of a common data collection and warehousing infrastructure (Jalapeno).

https://github.com/cisco-open/jalapeno/blob/main/README.md

Jalapeno breaks the data collection and warehousing problem down into a series of components and services:
- Data collector services such as GoBMP and Telegraf collect network topology and statistics and publish to Kafka
- Data processor services such as "Topology" (and other future services) subscribe to Kafka topics and write the data they receive to databases
- Arango GraphDB for modeling topology data
- InfluxDB for warehousing statistical time-series data
- API-Gateway: is currently under construction so for the lab we'll interact directly with the DB

#### Jalapeno Architecture and Data Flow
![jalapeno_architecture](https://github.com/cisco-open/jalapeno/blob/main/docs/diagrams/jalapeno_architecture.png)

One of the primary goals of the Jalapeno project is to be flexible and extensible. In the future we expect Jalapeno might support any number of data collectors and processors (LLDP Topology, pmacct, etc.). Or an operator might integrate Jalapeno's GoBMP/Topology/GraphDB modules into an existing environment running Kafka. We also envision future integrations with other API-driven data warehouses such as ThousandEyes: https://www.thousandeyes.com/

1. In a separate terminal session ssh to the Jalapeno VM 
```
cisco@198.18.128.101
pw = cisco123
```
2. Clone the Jalapeno repository at https://github.com/cisco-open/jalapeno, then cd into the repo and switch to the "cleu-srv6-lab" code branch:
```
git clone https://github.com/cisco-open/jalapeno.git
cd jalapeno
git checkout cleu-srv6-lab
```
Example output:
```
cisco@jalapeno:~/test$ git clone https://github.com/cisco-open/jalapeno.git
Cloning into 'jalapeno'...
remote: Enumerating objects: 4808, done.
remote: Counting objects: 100% (1468/1468), done.
remote: Compressing objects: 100% (566/566), done.
remote: Total 4808 (delta 733), reused 1350 (delta 670), pack-reused 3340
Receiving objects: 100% (4808/4808), 17.43 MiB | 26.88 MiB/s, done.
Resolving deltas: 100% (2461/2461), done.
cisco@jalapeno:~/test$ cd jalapeno/
cisco@jalapeno:~/test/jalapeno$ git checkout cleu-srv6-lab
Branch 'cleu-srv6-lab' set up to track remote branch 'cleu-srv6-lab' from 'origin'.
Switched to a new branch 'cleu-srv6-lab'
cisco@jalapeno:~/test/jalapeno$ 
```

3. Run the Jalapeno install script
```
cd install/
./deploy_jalapeno.sh 
```
Don't worry about the 'error validating' messages, they're cosmetic...we'll fix those one of these days

4. Verify k8s pods are running (note, some pods may initially be in a crashloop state. These should resolve after 2-3 minutes):
```
kubectl get pods -A
```
Expected output:
```
cisco@jalapeno:~/jalapeno/install$ kubectl get pods -A
NAMESPACE             NAME                                           READY   STATUS    RESTARTS        AGE
jalapeno-collectors   gobmp-5db68bd644-hzs82                         1/1     Running   3 (4m5s ago)    4m25s
jalapeno-collectors   telegraf-ingress-deployment-5b456574dc-wdhjk   1/1     Running   1 (4m2s ago)    4m25s
jalapeno              arangodb-0                                     1/1     Running   0               4m33s
jalapeno              grafana-deployment-565756bd74-x2szz            1/1     Running   0               4m32s
jalapeno              influxdb-0                                     1/1     Running   0               4m32s
jalapeno              kafka-0                                        1/1     Running   0               4m33s
jalapeno              lslinknode-edge-b954577f9-k8w6l                1/1     Running   4 (3m35s ago)   4m18s
jalapeno              telegraf-egress-deployment-5795ffdd9c-t8xrp    1/1     Running   2 (4m11s ago)   4m19s
jalapeno              topology-678ddb8bb4-rt9jg                      1/1     Running   3 (4m1s ago)    4m19s
jalapeno              zookeeper-0                                    1/1     Running   0               4m33s
kube-system           calico-kube-controllers-798cc86c47-d482k       1/1     Running   4 (16m ago)     14d
kube-system           calico-node-jd7cw                              1/1     Running   4 (16m ago)     14d
kube-system           coredns-565d847f94-fr8pp                       1/1     Running   4 (16m ago)     14d
kube-system           coredns-565d847f94-grmtl                       1/1     Running   4 (16m ago)     14d
kube-system           etcd-jalapeno                                  1/1     Running   5 (16m ago)     14d
kube-system           kube-apiserver-jalapeno                        1/1     Running   5 (16m ago)     14d
kube-system           kube-controller-manager-jalapeno               1/1     Running   6 (16m ago)     14d
kube-system           kube-proxy-pmwft                               1/1     Running   5 (16m ago)     14d
kube-system           kube-scheduler-jalapeno                        1/1     Running   6 (16m ago)     14d
```
5. Here are some additional k8s commands to try. Note the different outputs when specifying a particular namespace (-n option) vs. all namespaces (-A option):
```
kubectl get pods -n jalapeno
kubectl get pods -n jalapeno-collectors
kubectl get services -A
kubectl get all -A
kubectl get nodes
kubectl describe pod -n <namespace> <pod name>

example: kubectl describe pod -n jalapeno topology-678ddb8bb4-rt9jg
```
### Install Jalapeno SR-Processors
The SR-Processors are a pair of POC data processors that mine Jalapeno's graphDB and create a pair of new data collections. The sr-node processor loops through various link-state data collections and gathers relevant SR/SRv6 data for each node in the network. The sr-topology processor generates a graph of the entire network topology (internal and external links, nodes, peers, prefixes, etc.) and populates relevant SR/SRv6 data within the graph collection.

1. Install SR-Processors:
```
cd ~/SRv6_dCloud_Lab/lab_6/sr-processors
kubectl apply -f sr-node.yaml 
kubectl apply -f sr-topology.yaml 
```
2. Validate the pods are up and running:
```
kubectl get pods -n jalapeno
```
#### Expected output:
```
cisco@jalapeno:~/sr-processors$ kubectl get pods -n jalapeno
NAME                                          READY   STATUS    RESTARTS      AGE
arangodb-0                                    1/1     Running   0             12m
grafana-deployment-565756bd74-x2szz           1/1     Running   0             12m
influxdb-0                                    1/1     Running   0             12m
kafka-0                                       1/1     Running   0             12m
lslinknode-edge-b954577f9-k8w6l               1/1     Running   4 (11m ago)   12m
sr-node-8487488c9f-ftj59                      1/1     Running   0             40s     <--------
sr-topology-6b45d48c8-h8zns                   1/1     Running   0             33s     <--------
telegraf-egress-deployment-5795ffdd9c-t8xrp   1/1     Running   2 (12m ago)   12m
topology-678ddb8bb4-rt9jg                     1/1     Running   3 (11m ago)   12m
zookeeper-0                                   1/1     Running   0             12m
```

### BGP Monitoring Protocol (BMP)

Most transport SDN systems use BGP-LS to gather and model the underlying IGP topology. Jalapeno is intended to be a more generalized data platform to support use cases beyond internal transport such as VPNs or service chains. Because of this, Jalapeno's primary method of capturing topology data is via BMP. BMP supplies Jalapeno with all BGP AFI/SAFI info, and thus Jalapeno is able to model many different kinds of topology, including the topology of the Internet (at least from the perspective of our peering routers).

We'll first establish a BMP session between our route-reflectors and the open-source GoBMP collector (https://github.com/sbezverk/gobmp), which comes pre-packaged with the Jalapeno install. We'll then enable BMP on the RRs' BGP peering sessions with our PE routers xrd01 and xrd07. Once established, the RRs' will stream all BGP NLRI info they receive from the PE routers to the GoBMP collector, which will in turn publish the data to Kafka. We'll get more into the Jalapeno data flow in Lab 5.

1. BMP configuration on xrd05 and xrd06:
```
bmp server 1
 host 198.18.128.101 port 30511
 description jalapeno GoBMP  
 update-source MgmtEth0/RP0/CPU0/0
 flapping-delay 60
 initial-delay 5
 stats-reporting-period 60
 initial-refresh delay 25 spread 2
!
router bgp 65000
 neighbor 10.0.0.1
  bmp-activate server 1
 !
 neighbor fc00:0000:1111::1
  bmp-activate server 1
  !
 !
 neighbor 10.0.0.7
  bmp-activate server 1
 !
 neighbor fc00:0000:7777::1
  bmp-activate server 1
  !
 !
! 
```

2. Validate BMP session establishment and client monitoring:
```
show bgp bmp server 1
```

Expected output:
```
RP/0/RP0/CPU0:xrd05#show bgp bmp ser 1
Sat Jan  7 22:51:03.080 UTC
BMP server 1
Host 198.18.128.101 Port 30511
NOT Connected
Last Disconnect event received : 00:00:00
Precedence:  internet
BGP neighbors: 4
VRF: - (0x60000000)
Update Source: (null) (Mg0/RP0/CPU0/0)
Update Source Vrf ID: 0x0

Queue write pulse sent            : not set, not set (all)
Queue write pulse received        : not set
Update Mode : Route Monitoring Pre-Policy

TCP: 
  Last message sent: not set, Status: Not Connected
  Last write pulse received: not set, Waiting: FALSE

Message Stats:
Total msgs dropped   : 0
Total msgs pending   : 0, Max: 0 at not set
Total messages sent  : 0
Total bytes sent     : 0, Time spent: 0.000 secs
           INITIATION: 0
          TERMINATION: 0
         STATS-REPORT: 0
    PER-PEER messages: 0

ROUTE-MON messages   : 0

RP/0/RP0/CPU0:xrd05#sho bgp bmp ser 1
Sat Jan  7 23:16:46.761 UTC
BMP server 1
Host 198.18.128.101 Port 30511
Connected for 00:25:35
Last Disconnect event received : 00:00:00
Precedence:  internet
BGP neighbors: 4
VRF: - (0x60000000)
Update Source: 10.254.254.105 (Mg0/RP0/CPU0/0)
Update Source Vrf ID: 0x60000000

Queue write pulse sent            : Jan  7 23:15:58.131, Jan  7 22:51:26.348 (all)
Queue write pulse received        : Jan  7 23:15:58.131
Update Mode : Route Monitoring Pre-Policy

TCP: 
  Last message sent: Jan  7 23:15:58.131, Status: No Pending Data
  Last write pulse received: Jan  7 23:15:58.132, Waiting: FALSE

Message Stats:
Total msgs dropped   : 0
Total msgs pending   : 0, Max: 20 at Jan  7 22:51:26.146
Total messages sent  : 227
Total bytes sent     : 50522, Time spent: 0.003 secs
           INITIATION: 1
          TERMINATION: 0
         STATS-REPORT: 100
    PER-PEER messages: 126

ROUTE-MON messages   : 122

  Neighbor fc00:0:7777::1
Messages pending: 0
Messages dropped: 0
Messages sent   : 8
      PEER-UP   : 1
    PEER-DOWN   : 0
    ROUTE-MON   : 7

  Neighbor fc00:0:1111::1
Messages pending: 0
Messages dropped: 0
Messages sent   : 4
      PEER-UP   : 1
    PEER-DOWN   : 0
    ROUTE-MON   : 3

  Neighbor 10.0.0.7
Messages pending: 0
Messages dropped: 0
Messages sent   : 57
      PEER-UP   : 1
    PEER-DOWN   : 0
    ROUTE-MON   : 56

  Neighbor 10.0.0.1
Messages pending: 0
Messages dropped: 0
Messages sent   : 57
      PEER-UP   : 1
    PEER-DOWN   : 0
    ROUTE-MON   : 56
```

### Streaming Telemetry

Placeholder - do we bother with config, or simply explore the data in influx/grafana?



### Configure a BGP SRv6 locator
When we get to lab 6 we'll be sending SRv6 encapsulated traffic directly to/from Amsterdam and Rome. We'll need an SRv6 end.DT4/6 function at the egress nodes (xrd01 and xrd07) to be able to pop the SRv6 encap and perform a global table lookup on the underlying payload. Configuring an SRv6 locator under BGP will trigger creation of the end.DT4/6 functions:

1. Configure SRv6 locators for BGP on both xrd01 and xrd07:
```
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
   locator ISIS
  !
 !
 address-family ipv6 unicast
  segment-routing srv6
   locator ISIS
```

2. Validate end.DT4/6 SIDs belonging to BGP default table:
```
show segment-routing srv6 sid
```
Expected output on xrd01:
```
RP/0/RP0/CPU0:xrd01#show segment-routing srv6 sid
Sat Jan  7 22:24:00.280 UTC

*** Locator: 'ISIS' *** 

SID                         Behavior          Context                           Owner               State  RW
--------------------------  ----------------  --------------------------------  ------------------  -----  --
fc00:0:1111::               uN (PSP/USD)      'default':4369                    sidmgr              InUse  Y 
fc00:0:1111:e000::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:1111:e001::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
fc00:0:1111:e002::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
fc00:0:1111:e003::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
fc00:0:1111:e004::          uDT4              'carrots'                         bgp-65000           InUse  Y 
fc00:0:1111:e005::          uDT6              'carrots'                         bgp-65000           InUse  Y 
fc00:0:1111:e006::          uDT4              'default'                         bgp-65000           InUse  Y 
fc00:0:1111:e007::          uDT6              'default'                         bgp-65000           InUse  Y 
fc00:0:1111:e008::          uB6 (Insert.Red)  'srte_c_50_ep_fc00:0:7777::1' (50, fc00:0:7777::1)  xtc_srv6            InUse  Y 
fc00:0:1111:e009::          uB6 (Insert.Red)  'srte_c_40_ep_fc00:0:7777::1' (40, fc00:0:7777::1)  xtc_srv6            InUse  Y 
``` 

### End of lab 5
Please proceed to [Lab 6](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_6/lab_6-guide.md)