## Lab 5: Exploring Jalapeno, Kafka, and ArangoDB

### Description
In lab 5 we will install explore the Jalapeno system running on Kubernetes. We will log into the Kafka container and monitor topics for data coming in from Jalapeno's data collectors. We will spend some time getting familiar with the Arango graphDB, its data collections, its topology graphs, etc. Lastly we will populate the graphDB with some synthetic data and run a number of complex queries including graph traversals.

## Contents
1. [Kafka](#kafka
2. [Arango GraphDB](#arango-graphdb)
3. [BGP Monitoring Protocol](#bgp-monitoring-protocol-bmp)
4. [Streaming Telemetry](#streaming-telemetry)
5. [BGP SRv6 Locator](#configure-a-bgp-srv6-locator)

#### Continue on the Jalapeno VM

### Kafka:
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
### Arango GraphDB

Switch to web browser and connect to Jalapeno's Arango GraphDB
```
http://198.18.1.101:30852/

user: root
password: jalapeno
DB: jalapeno

```
#### Explore data collections

Run DB Queries:
```
for l in ls_node return l
```
Note: after running a query comment it out before running the next query. 

Example:

<img src="arango-query.png" width="600">

More sample queries:
```
for l in ls_link return l

for l in ls_link filter l.mt_id_tlv.mt_id !=2 return l

for l in ls_link filter l.mt_id_tlv.mt_id !=2 return { key: l._key, router_id: l.router_id, igp_id: l.igp_router_id, local_ip: l.local_link_ip, remote_ip: l.remote_link_ip }

for l in ls_node_edge return l

for l in sr_topology return l

for l in sr_node return { node: l.router_id, name: l.name, prefix_sid: l.prefix_attr_tlvs.ls_prefix_sid, srv6sid: l.srv6_sid }
```
### Populating the DB with external data 
Return to the Jalapeno VM ssh session and add some synthetic meta data to the DB:
```
cd ~/SRv6_dCloud_Lab/lab_4/
python3 add_meta_data.py
```
Validate meta data with ArangoDB query:
```
for l in sr_topology return { key: l._key, from: l._from, to: l._to, latency: l.latency, 
    utilization: l.percent_util_out, country_codes: l.country_codes }
```

Run the get_nodes.py script:
```
python3 get_nodes.py
cat nodes.json
```

### Graph traversals

Return to the ArangoDB browser UI and run a graph traversal from xrd01 to xrd07:
```
for v, e in outbound shortest_path 'sr_node/2_0_0_0000.0000.0001' TO 'sr_node/2_0_0_0000.0000.0007' sr_topology
    return  { node: v.name, location: v.location_id, address: v.address, prefix_sid: v.prefix_sid, srv6sid: v.srv6_sid }
```
Return path:
```
for v, e in outbound shortest_path 'sr_node/2_0_0_0000.0000.0007' TO 'sr_node/2_0_0_0000.0000.0001' sr_topology
    return  { node: v.name, location: v.location_id, address: v.address, prefix_sid: v.prefix_sid, srv6sid: v.srv6_sid }
```

Run a graph traversal from source prefix to destination prefix:
```
for v, e in outbound shortest_path 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' 
    TO 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7' sr_topology return  { node: v.name, 
    location: v.location_id, address: v.address, prefix_sid: v.prefix_sid, sid: v.srv6_sid, 
    latency: e.latency }
```
Return path:
```
for v, e in outbound shortest_path 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7' 
    TO 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' sr_topology return  { node: v.name, 
    location: v.location_id, address: v.address, prefix_sid: v.prefix_sid, sid: v.srv6_sid, 
    latency: e.latency }
```
These shortest path result are based purely on hop count. However, the graphDB allows us to run a 'weighted traversal' based on any metric or other piece of meta data in the graph.

### Graph traversals using metrics other than hop count

#### Query for the lowest latency path:
```
for v, e in outbound shortest_path 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' 
    TO 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7' sr_topology OPTIONS {weightAttribute: 'latency' } 
    return  { prefix: v.prefix, name: v.name, sid: e.srv6_sid, latency: e.latency }
```
Return path:
```
for v, e in outbound shortest_path 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7' 
    TO 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' sr_topology OPTIONS {weightAttribute: 'latency' } 
    return  { prefix: v.prefix, name: v.name, sid: e.srv6_sid, latency: e.latency }
```
#### Query for the least utilized path
Backups, data replication, other bulk transfers can oftentimes take a non-best path through the network.
Graph traversal query for the least utilized path:
```
FOR v, e, p IN 1..6 outbound 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' sr_topology 
    OPTIONS {uniqueVertices: "path", bfs: true} FILTER v._id == 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7' 
    RETURN { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, country_list: p.edges[*].country_codes[*],
    latency: sum(p.edges[*].latency), percent_util_out: avg(p.edges[*].percent_util_out)}
```
Return path:
```
FOR v, e, p IN 1..6 outbound 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7' sr_topology 
    OPTIONS {uniqueVertices: "path", bfs: true} FILTER v._id == 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' 
    RETURN { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, country_list: p.edges[*].country_codes[*],
    latency: sum(p.edges[*].latency), percent_util_out: avg(p.edges[*].percent_util_out)}
```
Note the Amsterdam to Rome path is different than the Rome to Amsterdam path

The previous queries provided paths up to 6-hops in length. We can increase or decrease the number of hops a graph traversal may use:

```
FOR v, e, p IN 1..5 outbound 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' sr_topology 
    OPTIONS {uniqueVertices: "path", bfs: true} FILTER v._id == 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7' 
    RETURN { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, country_list: p.edges[*].country_codes[*],
    latency: sum(p.edges[*].latency), percent_util_out: avg(p.edges[*].percent_util_out)}
```
Or
```
FOR v, e, p IN 1..8 outbound 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' sr_topology 
    OPTIONS {uniqueVertices: "path", bfs: true} FILTER v._id == 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7' 
    RETURN { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, country_list: p.edges[*].country_codes[*],
    latency: sum(p.edges[*].latency), percent_util_out: avg(p.edges[*].percent_util_out)}

```
### Data sovereignty

Find a suitable path that avoids France

```
for p in outbound k_shortest_paths  'sr_node/2_0_0_0000.0000.0001' TO 'unicast_prefix_v4/10.107.1.0_24_10.0.0.7'
    sr_topology filter p.edges[*].country_codes !like "%FRA%" return { path: p.edges[*].remote_node_name, 
    sid: p.edges[*].srv6_sid, country_list: p.edges[*].country_codes[*], latency: sum(p.edges[*].latency),
    percent_util_out: avg(p.edges[*].percent_util_out)}
```

### End of lab 5
Please proceed to [Lab 6](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_6/lab_6-guide.md)