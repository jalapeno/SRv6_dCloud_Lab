## Lab 6: Exploring Jalapeno, Kafka, and ArangoDB

### Description
In lab 6 we will explore the Jalapeno system running on Kubernetes. We will log into the Kafka container and monitor topics for data coming in from Jalapeno's data collectors, which will then be picked up by Jalapeno processors (topology, lslinknode, sr-node, sr-topology, etc.). We will spend some time getting familiar with the Arango graphDB, its data collections, and run some basic queries. Lastly we will populate the graphDB with some synthetic data and run a number of complex queries including graph traversals.

## Contents
1. [Kafka](#kafka)
2. [Arango GraphDB](#arango-graphdb)
3. [Basic queries](#basic-queries-to-explore-data-collections)
4. [Populating the DB with meta data](#populating-the-db-with-external-data)
5. [Graph Traversals](#graph-traversals)

#### Continue on the Jalapeno VM

### Kafka
From the Kafka homepage: Apache Kafka is an open-source distributed event streaming platform used by thousands of companies for high-performance data pipelines, streaming analytics, data integration, and mission-critical applications.
https://kafka.apache.org/

1. Login to the Kafka container and list topics:
```
kubectl exec -it kafka-0 /bin/bash -n jalapeno

cd bin
unset JMX_PORT

./kafka-topics.sh --list  --bootstrap-server localhost:9092
```
A few seconds after running the command you should see the following list toward the bottom on the command output:
```
gobmp.parsed.evpn
gobmp.parsed.evpn_events
gobmp.parsed.flowspec
gobmp.parsed.flowspec_events
gobmp.parsed.flowspec_v4
gobmp.parsed.flowspec_v4_events
gobmp.parsed.flowspec_v6
gobmp.parsed.flowspec_v6_events
gobmp.parsed.l3vpn
gobmp.parsed.l3vpn_events
gobmp.parsed.l3vpn_v4
gobmp.parsed.l3vpn_v4_events
gobmp.parsed.l3vpn_v6
gobmp.parsed.l3vpn_v6_events
gobmp.parsed.ls_link
gobmp.parsed.ls_link_events
gobmp.parsed.ls_node
gobmp.parsed.ls_node_events
gobmp.parsed.ls_prefix
gobmp.parsed.ls_prefix_events
gobmp.parsed.ls_srv6_sid
gobmp.parsed.ls_srv6_sid_events
gobmp.parsed.peer
gobmp.parsed.peer_events
gobmp.parsed.sr_policy
gobmp.parsed.sr_policy_events
gobmp.parsed.sr_policy_v4
gobmp.parsed.sr_policy_v4_events
gobmp.parsed.sr_policy_v6
gobmp.parsed.sr_policy_v6_events
gobmp.parsed.unicast_prefix
gobmp.parsed.unicast_prefix_events
gobmp.parsed.unicast_prefix_v4
gobmp.parsed.unicast_prefix_v4_events
gobmp.parsed.unicast_prefix_v6
gobmp.parsed.unicast_prefix_v6_events
jalapeno.ls_node_edge_events
jalapeno.telemetry
```

2. Monitor a Kafka topic:
```
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_node
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_link
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.l3vpn_v4

./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic jalapeno.telemetry
```
The gobmp topics should be fairly quiet unless BGP updates are happening. Try clearing bgp-ls or bgp-vpnv4 on one of the RRs and see what data comes through on the Kafka topic.

```
clear bgp vpnv4 unicast * soft
clear bgp link-state link-state * soft
```

Example GoBMP message published to Kafka when monitoring the l3vpn_v4 topic and clearing bgp-vpnv4 on xrd05:
```
{"action":"add","router_hash":"0669df0f031fb83e345267a9679bbc6a","router_ip":"10.0.0.5","base_attrs":{"base_attr_hash":"b41cebdba45850cdb7f6994b4675fa4c","origin":"incomplete","local_pref":100,"is_atomic_agg":false,"ext_community_list":["rt=9:9"]},"peer_hash":"e0b24585a43db7cc196f5e42d48e8b5f","peer_ip":"fc00:0:1111::1","peer_asn":65000,"timestamp":"2023-01-08T04:22:14.000588527Z","prefix":"10.9.1.0","prefix_len":24,"is_ipv4":true,"nexthop":"fc00:0:1111::1","is_nexthop_ipv4":false,"labels":[14681088],"is_prepolicy":false,"is_adj_rib_in":false,"vpn_rd":"10.0.0.1:0","vpn_rd_type":1,"prefix_sid":{"srv6_l3_service":{"sub_tlvs":{"1":[{"sid":"fc00:0:1111::","endpoint_behavior":63,"sub_sub_tlvs":{"1":[{"locator_block_length":32,"locator_node_length":16,"function_length":16,"argument_length":0,"transposition_length":16,"transposition_offset":48}]}}]}}}}
```

### Arango GraphDB

1. Switch to a web browser and connect to Jalapeno's Arango GraphDB
```
http://198.18.128.101:30852/

user: root
password: jalapeno
DB: jalapeno

```
2. Spend some time exploring the data collections in the DB

#### Basic queries to explore data collections 

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
cd ~/SRv6_dCloud_Lab/lab_7/
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

### End of lab 6
Please proceed to [Lab 7](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_7/lab_7-guide.md)