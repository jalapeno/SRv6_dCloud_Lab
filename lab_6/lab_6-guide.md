## Lab 6: Exploring Jalapeno, Kafka, and ArangoDB

### Description
In lab 6 we will explore the Jalapeno system running on Kubernetes. We will log into the Kafka container and monitor topics for data coming in from Jalapeno's data collectors. Data which is subsequently picked up by Jalapeno's data processors (topology, lslinknode, sr-node, sr-topology, etc.) and written to the Arango graphDB. We will spend some time getting familiar with ArangoDB and the Jalapeno data collections, and will run some basic queries. Lastly we will populate the graphDB with some synthetic data and run a number of complex queries including graph traversals.

## Contents
1. [Lab Objectives](#lab-objectives)
2. [Kafka](#kafka)
3. [Arango GraphDB](#arango-graphdb)
4. [Basic queries](#basic-queries-to-explore-data-collections)
5. [Populating the DB with meta data](#populating-the-db-with-external-data)
6. [Graph Traversals and Shortest Path Queries](#arango-graph-traversals-and-shortest-path-queries)
7. [Shortest Path Using Other Metrics](#shortest-path-queries-using-metrics-other-than-hop-count)
8. [Shortest Path using Graph Traversal](#graph-traversals)
9. [K Shortest Paths](#k-shortest-paths)

## Lab Objectives
The student upon completion of Lab 6 should have achieved the following objectives:

* A tour of the Jalapeno platform and high level understanding of how it collects and processes data
* Familiarity with the ArangoDB UI and the BMP/BGP data collections the system has created
* Familiarity with Arango Query Language (AQL) syntax
* Familiarity with more complex Arango shortest-path and graph traversal queries

### Kafka
From the Kafka homepage: Apache Kafka is an open-source distributed event streaming platform used by thousands of companies for high-performance data pipelines, streaming analytics, data integration, and mission-critical applications.
https://kafka.apache.org/

Jalapeno's data collectors publish their data to Kafka topics. Jalapeno's data processors subscribe to the relevant Kafka topics, gather the published data, and write it to either the graphDB or TSDB. This Collector -> Kafka -> Processor -> DB pipeline allows for architectural flexibility such that other applications could subscribe to the Jalapeno topics and use the BMP or telemetry data for their own purposes.

#### Continue on the Jalapeno VM

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
 - ISIS node data (via BGP-LS NLRIs) is published to the ls_node topic:
```
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_node
```
 - ISIS link, prefix, and SRv6 SID data is published to the ls_link, ls_prefix, and ls_srv6_sid topics respectively:
```
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_link
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_prefix
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.ls_srv6_sid
```
 - L3VPN prefix data is published to the l3vpn topics:
```
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic gobmp.parsed.l3vpn_v4
```
 - We won't be using streaming telemetry in this lab, however MDT is configured on the nodes in the lab and the Telegraf collector publishes the data to the jalapeno.telemetry topic:
```
./kafka-console-consumer.sh --bootstrap-server localhost:9092  --topic jalapeno.telemetry
```

3. The gobmp topics should be fairly quiet unless BGP updates are happening. Try clearing bgp-ls or bgp-vpnv4 on one of the RRs and see what data comes through when monitoring the Kafka topic.

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
The ArangoDB Query Language (AQL) can be used to retrieve and modify data that are stored in ArangoDB.

The general workflow when executing a query is as follows:

 - A client application ships an AQL query to the ArangoDB server. The query text contains everything ArangoDB needs to compile the result set

 - ArangoDB will parse the query, execute it and compile the results. If the query is invalid or cannot be executed, the server will return an error that the client can process and react to. If the query can be executed successfully, the server will return the query results (if any) to the client

https://www.arangodb.com/docs/stable/aql/index.html


3. Run some DB Queries:
```
for l in ls_node return l
```
Note: after running a query you will need to comment it out before running the next query. 

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

The add_meta_data.py python script will connect to the ArangoDB and populate elements in our data collections with addresses and country codes. Also, due to the fact that we can't run realistic traffic through the xrd topology the script will populate the relevant graphDB elements with synthetic link latency and utilization data per this diagram:

<img src="latency-util.png" width="600">

1. Return to the ssh session on the Jalapeno VM and add some synthetic meta data to the DB:
```
cd ~/SRv6_dCloud_Lab/lab_6/
python3 add_meta_data.py
```

2. Validate meta data with ArangoDB query:
```
for l in sr_topology return { key: l._key, from: l._from, to: l._to, latency: l.latency, 
    utilization: l.percent_util_out, country_codes: l.country_codes }
```
 - Note: only the ISIS links in the DB have latency and utilization numbers. The Amsterdam and Rome VMs are directly connected to PEs xrd01 and xrd07, so their "edge connections" in the DB are effectively zero latency.

3. Run the get_nodes.py script to get a listing of nodes in the network, their addresses, and SR/SRv6 SID data:
```
python3 get_nodes.py
cat nodes.json
```

### Arango Graph traversals and shortest path queries
https://www.arangodb.com/docs/stable/aql/graphs.html

#### Shortest Path
This type of query is supposed to find the shortest path between two given documents (startVertex and targetVertex) in your graph. In our case the shortest path between two different nodes in graph's representation of the network.

1. Return to the ArangoDB browser UI and run a shortest path query from xrd01 to xrd07, and have it return SR and SRv6 SID data:
```
for v, e in outbound shortest_path 'sr_node/2_0_0_0000.0000.0001' TO 'sr_node/2_0_0_0000.0000.0007' sr_topology return  { node: v.name, location: v.location_id, address: v.address, prefix_sid: v.prefix_sid, srv6sid: v.srv6_sid }
```
2. Run the query against the return path:
```
for v, e in outbound shortest_path 'sr_node/2_0_0_0000.0000.0007' TO 'sr_node/2_0_0_0000.0000.0001' sr_topology return  { node: v.name, location: v.location_id, address: v.address, prefix_sid: v.prefix_sid, srv6sid: v.srv6_sid }
```

3. Run a shortest path query from source prefix (Amsterdam) to destination prefix (Rome):
```
 for v, e in any shortest_path 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' TO 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7' sr_topology return  { node: v.name, location: v.location_id, address: v.address, prefix_sid: v.prefix_sid, sid: v.srv6_sid, latency: e.latency }
```
4. Query for the return path:
```
for v, e in outbound shortest_path 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7' TO 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' sr_topology return  { node: v.name, location: v.location_id, address: v.address, prefix_sid: v.prefix_sid, sid: v.srv6_sid, latency: e.latency }
```
These shortest path result are based purely on hop count. Also, in the case of multiple equal cost shortest paths, the Arango query will return the first one it finds. 

Basic shortest path by hop count is fine, however, the graphDB also allows us to run a 'weighted shortest path query' based on any metric or other piece of meta data in the graph!

### Shortest path queries using metrics other than hop count

#### Query for the lowest latency path:
```
for v, e in outbound shortest_path 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' TO 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7' sr_topology OPTIONS {weightAttribute: 'latency' } return  { prefix: v.prefix, name: v.name, sid: e.srv6_sid, latency: e.latency }
```
Return path:
```
for v, e in outbound shortest_path 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7' TO 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' sr_topology OPTIONS {weightAttribute: 'latency' } return { prefix: v.prefix, name: v.name, sid: e.srv6_sid, latency: e.latency }
```
### Graph Traversals
A traversal starts at one specific document (startVertex) and follows all edges connected to this document. For all documents (vertices) that are targeted by these edges it will again follow all edges connected to them and so on. It is possible to define how many of these follow iterations should be executed at least (min depth) and at most (max depth).
https://www.arangodb.com/docs/stable/aql/graphs-traversals-explained.html

For our purposes we can use Graph Traversal to run a limited or bounded shortest path query (min and max hops):

#### Query for the least utilized path
Backups, data replication, other bulk transfers can oftentimes take a non-best path through the network. In theory the least utilized path could be many hops in length, so we're going to build the query such that the traversal limits itself to a maximum of 6 hops from the source vertex.

1. Graph traversal query for the least utilized path:
```
FOR v, e, p IN 1..6 outbound 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' sr_topology 
    OPTIONS {uniqueVertices: "path", bfs: true} FILTER v._id == 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7' 
    RETURN { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, country_list: p.edges[*].country_codes[*],
    latency: sum(p.edges[*].latency), percent_util_out: avg(p.edges[*].percent_util_out)}
```
 - Note the least utilized path should be xrd01 -> xrd02 -> xrd03 -> xrd04 -> xrd07. This also happens to be the longest path geographically in our network (Netherlands proceeding east and south through Germany, Poland, Ukraine, Turkey, etc.). Any traffic taking this path will be subject to the longest latency in our network.

2. Query for the return path:
```
FOR v, e, p IN 1..6 outbound 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7' sr_topology 
    OPTIONS {uniqueVertices: "path", bfs: true} FILTER v._id == 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' 
    RETURN { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, country_list: p.edges[*].country_codes[*],
    latency: sum(p.edges[*].latency), percent_util_out: avg(p.edges[*].percent_util_out)}
```
 - Note: unlike latency, where latency will be roughly equivalent in either direction, average utilization could be quite different. In our network the least utilized Amsterdam to Rome path is different from the least utilized Rome to Amsterdam path: xrd07 -> xrd06 -> xrd02 -> xrd01

The previous queries provided paths up to 6-hops in length. We can increase or decrease the number of hops a graph traversal may use

3. Decrease the length of the traversal (should provide fewer valid results)

```
FOR v, e, p IN 1..5 outbound 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' sr_topology 
    OPTIONS {uniqueVertices: "path", bfs: true} FILTER v._id == 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7' 
    RETURN { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, country_list: p.edges[*].country_codes[*],
    latency: sum(p.edges[*].latency), percent_util_out: avg(p.edges[*].percent_util_out)}
```
4. Increase the length of the traversal (should provide more valid results)
```
FOR v, e, p IN 1..8 outbound 'unicast_prefix_v4/10.101.1.0_24_10.0.0.1' sr_topology 
    OPTIONS {uniqueVertices: "path", bfs: true} FILTER v._id == 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7' 
    RETURN { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, country_list: p.edges[*].country_codes[*],
    latency: sum(p.edges[*].latency), percent_util_out: avg(p.edges[*].percent_util_out)}

```
 - Note: the graph traversal is inherently loop-free. If you increase the previous query to max of 10 or 12 hops you should get back the same number of results as 8 hops max.

### K Shortest Paths
This type of query finds the first k paths in order of length (or weight) between two given documents, startVertex and targetVertex in your graph.

https://www.arangodb.com/docs/stable/aql/graphs-kshortest-paths.html

#### A Data sovereignty query

1. We'll use the K Shortest Paths query method to find one or more suitable paths from Amsterdam to Rome that avoids France:

```
for p in outbound k_shortest_paths  'sr_node/2_0_0_0000.0000.0001' TO 'unicast_prefix_v4/20.0.0.0_24_10.0.0.7'
    sr_topology filter p.edges[*].country_codes !like "%FRA%" return { path: p.edges[*].remote_node_name, 
    sid: p.edges[*].srv6_sid, country_list: p.edges[*].country_codes[*], latency: sum(p.edges[*].latency),
    percent_util_out: avg(p.edges[*].percent_util_out)}
```
 - The results in the query response should not traverse any links containing the FRA country code

### End of lab 6
Please proceed to [Lab 7](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_7/lab_7-guide.md)