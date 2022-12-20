import subprocess
from tabnanny import check
from .pkg import arangodb
from util import connections
from copy import copy
from math import ceil
from configs import influxconfig, arangoconfig, routerconfig
import json
import logging

logging.basicConfig(filename='srte.log', level=logging.DEBUG)

def low_latency_traverse(prefix_split, dest_prefix):
    influx_connection, arango_connection = connections.InfluxConn(), connections.ArangoConn()
    #influx_client = influx_connection.connect_influx(influxconfig.host, influxconfig.port, influxconfig.user, influxconfig.password, influxconfig.dbname)
    arango_client = arango_connection.connect_arango(arangoconfig.url, arangoconfig.database, arangoconfig.username, arangoconfig.password)

    latency_key = "latency"
    epe_key = "epe_sid"

    logging.info("""
Getting latency to prefix via EPE points: 
    """)
    external_latency = arangodb.external_latencies(arango_client, prefix_split)
    ext_latency = list(external_latency)
    # if the DB does not contain a latency value (aka None) for a given EPE-to-prefix, set latency = 0
    for i in ext_latency:
        for k, v in i.items():
            if v is None:
                i[k] = 0
  
    sorted_by_latency = sorted(ext_latency, key=lambda d: d['latency'])
    logging.info("json: %s", json.dumps(sorted_by_latency, sort_keys=False, indent=4))
    logging.info("lowest latency: %s",sorted_by_latency[0])

    aql_to = sorted_by_latency[0]['epe_prefix']

    weighted_traversal = arangodb.weighted_traversal(arango_client, aql_to)
    logging.info("""Weighted traversal - shortest path using link latency metric: 
    """)
    wt = list(weighted_traversal)
    logging.info("json: %s", json.dumps(wt, sort_keys=False, indent=4))

    latency_values = [a_dict[latency_key] for a_dict in weighted_traversal]
    latency_values =  [x for x in latency_values if type(x) == int]
    #print("Latency value at each hop: ", latency_values)
    path_latency = sum(latency_values)
    logging.info("Total path latency: %s", path_latency)
    hop_count = len(latency_values)
    logging.info("Hop count: %s", hop_count)
    wp = ceil(hop_count/2)
    logging.info("PQ hop: %s", wp) 

    epe_sid_list = [a_dict[epe_key] for a_dict in weighted_traversal]
    logging.info("epe sids: %s", epe_sid_list)
    remove = None
    epe_sid_list = [value for value in epe_sid_list if value != remove]
    epe_sid = epe_sid_list[0]
    logging.info("epe_sid: %s", epe_sid)
 
    pq_node = (weighted_traversal[wp])
    logging.info("""PQ node: 
    """)
    logging.info("json: %s", json.dumps(pq_node, sort_keys=False, indent=4))
    pq_node_key = pq_node['node']
    #print("PQ node key: ", pq_node_key)

    pq_node_obj = arangodb.get_ls_node(arango_client, pq_node_key)
    logging.info("pq node prefix and srgb: %s", pq_node_obj)
    prefix_key = "prefix"
    pq_node_prefix = [a_dict[prefix_key] for a_dict in pq_node_obj]
    pq_prefix = pq_node_prefix[0]
    #print("pq node prefix: ", pq_prefix)
    
    sid_index = arangodb.get_prefix_sid(arango_client, pq_prefix)
    srgb_key = "srgb_start"
    srgb = [a_dict[srgb_key] for a_dict in pq_node_obj]
    srgb_list = srgb[0]
    srgb_start = srgb_list[0]
    pq_prefix_sid = sid_index + srgb_start 
    print("pq sid index: {}, srgb start: {}, and prefix sid: {}, " .format(sid_index, srgb_start, pq_prefix_sid))

    asn = "asn"
    asn_list = [a_dict[asn] for a_dict in weighted_traversal]
    asn_list =  [x for x in asn_list if type(x) == int]
    internal_hop_count = len(asn_list)
    logging.info("Internal network hops: %s", internal_hop_count)
    last_hop = (weighted_traversal[internal_hop_count - 1])
    logging.info("""last internal hop: 
    """)
    logging.info("json: %s", json.dumps(last_hop, sort_keys=False, indent=4))
    last_hop_key = last_hop['node']
    logging.info("last hop key: %s", last_hop_key)
    
    last_hop_prefix_obj = arangodb.get_ls_node(arango_client, last_hop_key)
    logging.info("last hop prefix and srgb: %s", last_hop_prefix_obj)
    last_hop_prefix = [a_dict[prefix_key] for a_dict in last_hop_prefix_obj]
    lh_prefix = last_hop_prefix[0]
    logging.info("last hop prefix: %s", lh_prefix)
    sid_index = arangodb.get_prefix_sid(arango_client, lh_prefix)
    srgb_key = "srgb_start"
    srgb = [a_dict[srgb_key] for a_dict in last_hop_prefix_obj]
    srgb_list = srgb[0]
    srgb_start = srgb_list[0]
    last_hop_prefix_sid = sid_index + srgb_start 
    logging.info("last hop sid index: {}, srgb start: {}, and prefix sid: {}, " .format(sid_index, srgb_start, last_hop_prefix_sid))
    print("last hop sid index: {}, srgb start: {}, and prefix sid: {}, " .format(sid_index, srgb_start, last_hop_prefix_sid))

    if pq_prefix_sid == last_hop_prefix_sid:
        logging.info("SR and EPE label stack: %s, %s", last_hop_prefix_sid, epe_sid)

        print('vppctl command: sudo vppctl ip route add', dest_prefix, 'via 10.0.7.1 GigabitEthernet0/7/0 out-labels', \
        last_hop_prefix_sid, epe_sid)
        subprocess.call(['sudo', 'vppctl', 'sr steer del l3', dest_prefix])
        subprocess.call(['sudo', 'vppctl', 'ip', 'route', 'add', dest_prefix, 'via', '10.0.7.1', 'GigabitEthernet0/7/0', \
        'out-labels', str(last_hop_prefix_sid), str(epe_sid)]) 
        
    else:
        logging.info("SR label stack: %s, %s, %s", pq_prefix_sid, last_hop_prefix_sid, epe_sid)
        print("""
        """)
        print('vppctl command: sudo vppctl ip route add', dest_prefix, 'via 10.0.7.1 GigabitEthernet0/7/0 out-labels', \
        pq_prefix_sid, last_hop_prefix_sid, epe_sid) 
        subprocess.call(['sudo', 'vppctl', 'sr steer del l3', dest_prefix])
        subprocess.call(['sudo', 'vppctl', 'ip', 'route', 'add', dest_prefix, 'via', '10.0.7.1', 'GigabitEthernet0/7/0', \
        'out-labels', str(pq_prefix_sid), str(last_hop_prefix_sid), str(epe_sid)])
    
    print('vppctl show ip fib: ', dest_prefix)
    subprocess.call(['sudo', 'vppctl', 'show', 'ip', 'fib', dest_prefix])
    
    ### The above pq calculation is POC quality and does not work properly for all topologies
    # if wp > p:
    #     pq_node = (weighted_traversal[wp])
    #     pq_node_key = pq_node['node']
    #     pq_node_prefix = arangodb.get_lsnode(arango_client, pq_node_key)
    #     print("lsnode prefix: ", pq_node_prefix)
    
    #     sid_index = arangodb.get_prefix_sid(arango_client, pq_node_prefix)
    #     prefix_sid = [x+routerconfig.srgb_start for x in sid_index]
    #     print("prefix_sid: ", prefix_sid[0])
    # else:
    #     pq_node = (weighted_traversal[3])
    #     pq_node_key = pq_node['node']

    #     pq_node_prefix = arangodb.get_lsnode(arango_client, pq_node_key)
    #     print("lsnode prefix: ", pq_node_prefix)
    
    #     sid_index = arangodb.get_prefix_sid(arango_client, pq_node_prefix)
    #     prefix_sid = [x+routerconfig.srgb_start for x in sid_index]
    #     print("prefix_sid: ", prefix_sid[0])
    
if __name__ == '__low_latency_traverse__':
    low_latency_traverse()