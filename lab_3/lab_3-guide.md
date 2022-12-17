### Configure BGP Monitoring Protocol (BMP) and Install open-source Jalapeno package

R05
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
 neighbor fc00:0:1::1
  bmp-activate server 1
  !
 !
 neighbor 10.0.0.7
  bmp-activate server 1
 !
 neighbor fc00:0:7::1
  bmp-activate server 1
  !
 !
! 

```

R06
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
 neighbor fc00:0:1::1
  bmp-activate server 1
  !
 !
 neighbor 10.0.0.7
  bmp-activate server 1
 !
 neighbor fc00:0:7::1
  bmp-activate server 1
  !
 !
! 

```

Validate changes:
```
ping 198.18.128.101
show bgp bmp server 1
```

Expected output:
```
RP/0/RP0/CPU0:xrd06#ping 198.18.128.101
Wed Dec 14 23:00:18.649 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 198.18.128.101, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/7 ms

RP/0/RP0/CPU0:xrd06#sho bgp bmp ser 1  
Wed Dec 14 23:24:01.861 UTC
BMP server 1
Host 198.18.128.101 Port 30511
Connected for 00:01:18
...
```
### Install Jalapeno 

1. ssh to the Jalapeno VM cisco@198.18.1.101 (pw = cisco123)
2. Clone the Jalapeno repository at https://github.com/cisco-open/jalapeno and switch to the cleu-srv6-lab code branch:
```
git clone https://github.com/cisco-open/jalapeno.git

git checkout cleu-srv6-lab

```

3. Run the Jalapeno install script
```
cd jalapeno/install/

./deploy_jalapeno.sh 

# Expected output:

Creating Jalapeno Namespace
namespace/jalapeno created
Creating Jalapeno Service Account
serviceaccount/jalapeno created
clusterrole.rbac.authorization.k8s.io/jalapeno created
clusterrolebinding.rbac.authorization.k8s.io/jalapeno created
Setting up secret for docker.io
secret/regcred created
Deploying Kafka
persistentvolume/pvzoo created
persistentvolume/pvkafka created
service/zookeeper created
statefulset.apps/zookeeper created
configmap/broker-config created
service/broker created
service/kafka created
statefulset.apps/kafka created
error: resource mapping not found for name: "zookeeper-pdb" namespace: "jalapeno" from "/home/cisco/jalapeno/install/infra/kafka/1-zookeeper.yaml": no matches for kind "PodDisruptionBudget" in version "policy/v1beta1"
ensure CRDs are installed first
Deploying ArangoDB
persistentvolume/arangodb-apps created
persistentvolume/arangodb created
statefulset.apps/arangodb created
service/arangodb created
service/arango-np created
Deploying InfluxDB
statefulset.apps/influxdb created
service/influxdb created
service/influxdb-np created
Deploying Grafana
configmap/grafana-config created
deployment.apps/grafana-deployment created
service/grafana created
service/grafana-np created
error validating "/home/cisco/jalapeno/install/infra/grafana/egress-mdt.json": error validating data: [apiVersion not set, kind not set]; if you choose to ignore these errors, turn validation off with --validate=false
error validating "/home/cisco/jalapeno/install/infra/grafana/ingress-mdt.json": error validating data: [apiVersion not set, kind not set]; if you choose to ignore these errors, turn validation off with --validate=false
Finished deploying infra services
Deploying Jalapeno Collectors
Creating jalapeno-collectors namespace
namespace/jalapeno-collectors created
Deploying Telegraf-Ingress Collector to collect network performance-metric data
configmap/telegraf-ingress-config created
deployment.apps/telegraf-ingress-deployment created
service/telegraf-ingress-np created
Deploying GoBMP Collector to collect network topology data
configmap/gobmp-config created
service/gobmp created
deployment.apps/gobmp created
Finished deploying Jalapeno Collectors
Deploying Topology
secret/jalapeno created
deployment.apps/topology created
Deploying Telegraf-Egress
configmap/telegraf-egress-config created
deployment.apps/telegraf-egress-deployment created
Deploying LS Link-Node Edge Processor
deployment.apps/lslinknode-edge created

```
4. Verify k8s pods are running:
```
kubectl get pods -A

or

kubectl get pods -n jalapeno
kubectl get pods -n jalapeno-collectors
```
ssh to the Jalapeno VM and run some Kubectl commands
```
ssh cisco@198.18.1.101

kubectl get all -A
kubectl get pods -n jalapeno
kubectl get pods -n jalapeno-collectors
kubectl get services -A

```
Kafka:
1. List Kafka topics
2. Listen to Kafka topics
```
kubectl exec -it kafka-0 /bin/bash -n jalapeno

cd bin
unset JMX_PORT

./kafka-topics.sh --list  --bootstrap-server localhost:9092
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_node
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_link
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.l3vpn_v4

./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic jalapeno.telemetry

```


Connect to Jalapeno's Arango GraphDB
```
http://198.18.1.101:30852/

user: root
password: jalapeno
DB: jalapeno

```
Explore data collections

Run DB Queries:
```
for l in ls_node return l
```
note: after running a query comment it out before running the next query. Example:

<img src="arango-query.png" width="600">

More queries:
```
for l in ls_link return l

for l in ls_link filter l.mt_id_tlv.mt_id !=2 return l

for l in ls_link filter l.mt_id_tlv.mt_id !=2 return { key: l._key, router_id: l.router_id, igp_id: l.igp_router_id, local_ip: l.local_link_ip, remote_ip: l.remote_link_ip }

for l in ls_node_edge return l

for l in sr_topology return l

for l in sr_node return { node: l.router_id, name: l.name, prefix_sid: l.prefix_attr_tlvs.ls_prefix_sid, srv6sid: l.srv6_sid }
```

Add some synthetic data:
```
python script

```
Run some more queries
```
for v, e in outbound shortest_path 'sr_node/2_0_0_0000.0000.0001' TO 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7' sr_topology return  { name: v.name, sid: e.srv6_sid, latency: e.latency }



```