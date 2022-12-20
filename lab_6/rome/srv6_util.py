import subprocess
from .pkg import arangodb
from util import connections
from math import ceil
from configs import arangoconfig
import json
import logging

logging.basicConfig(filename='srte.log', level=logging.DEBUG)

def srv6_util(prefix_split, dest_prefix):
    arango_connection = connections.ArangoConn()
    arango_client = arango_connection.connect_arango(arangoconfig.url, arangoconfig.database, arangoconfig.username, arangoconfig.password)

    util_key = "percent_util_out"
    router_id_key = "node"

    srv6_util = arangodb.srv6_util(arango_client)
    print("srv6_util: ", srv6_util)
    sorted_by_util = sorted(srv6_util, key=lambda d: d[util_key])
    logging.info("util sort: %s", json.dumps(sorted_by_util, sort_keys=False, indent=4))
    
    util_values = [a_dict[util_key] for a_dict in sorted_by_util]
    logging.info("Avg util along path: %s", (util_values))

    minUtil = min(sorted_by_util, key=lambda x:x[util_key])
    hops = (minUtil[router_id_key])

    internal_hops = list(filter(None, hops))
    logging.info("least util internal hops: %s", internal_hops)

    # PQ node calculation
    hop_count = len(internal_hops)
    logging.info("Hop count: %s ", hop_count)
    wp = ceil((hop_count/2))#-1)
    logging.info("PQ hop: %s ", wp) 
    pq_node = (internal_hops[wp])
    logging.info("PQ node: %s", pq_node)
    pq_srv6_sid = arangodb.get_srv6_sid(arango_client, pq_node)
    logging.info("pq srv6 locator: %s ", pq_srv6_sid)
    pq_srv6_sid = arangodb.get_srv6_sid(arango_client, pq_node)
    logging.info("pq srv6 locator: %s ", pq_srv6_sid)

    #PQ node calculation for shortest path by hop count. We want to make sure to avoid this path in the demo.
    shortest_path = min(sorted_by_util, key=lambda x:x[router_id_key])
    sp_hops = (shortest_path[router_id_key])
    logging.info("shortest_path: %s", sp_hops)
    sp_count = len(sp_hops)
    logging.info("Shortest path hop count: %s ", sp_count)
    sp_wp = ceil((sp_count/2)-1)
    logging.info("SP PQ hop: %s ", sp_wp) 
    sp_pq_node = (internal_hops[sp_wp])
    logging.info("SP PQ node: %s", sp_pq_node)
    sp_srv6_sid = arangodb.get_srv6_sid(arango_client, sp_pq_node)
    logging.info("SP srv6 locator: %s ", sp_srv6_sid)

    last_hop = internal_hops[-1]
    logging.info("Last hop: %s", last_hop)
    lh_srv6_sid = arangodb.get_srv6_sid(arango_client, last_hop)
    logging.info("LH srv6 locator: %s ", lh_srv6_sid)

    split_horizon = arangodb.split_horizon(arango_client, pq_node, last_hop, wp)
    logging.info("split horizon: %s ", split_horizon)

    usid_block = "fc00:0:"
    sp_usid_list = sp_srv6_sid.split(usid_block)
    sp_usid = sp_usid_list[1]
    sp_usid_int = sp_usid.split(':')
    sp_usid_str = sp_usid_int[0]

    pq_usid_list = pq_srv6_sid.split(usid_block)
    pq_usid = pq_usid_list[1]
    pq_usid_int = pq_usid.split(':')
    pq_usid_str = pq_usid_int[0]

    lh_usid_list = lh_srv6_sid.split(usid_block)
    lh_usid = lh_usid_list[1]
    lh_usid_int = lh_usid.split(':')
    lh_usid_str = lh_usid_int[0]

    ipv6_separator = ":"
    if pq_srv6_sid == lh_srv6_sid:
        usid_stack = usid_block+sp_usid_str+lh_usid_str+ipv6_separator+ipv6_separator
        logging.info("pq and lh srv6 sid are the same: %s ", usid_stack)
    else:
        usid_stack = usid_block+sp_usid_str+ipv6_separator+pq_usid_str+ipv6_separator+lh_usid_str+ipv6_separator+ipv6_separator
    logging.info("srv6 sid: %s ", usid_stack)

    #return path_latency
    logging.info("vppctl: vppctl sr policy add bsid 101::101 next %s", usid_stack)
    logging.info("encap")
    print('vppctl: vppctl sr steer l3', dest_prefix, 'via bsid 101::101')
    subprocess.call(['sudo', 'vppctl', 'ip route del', dest_prefix])
    subprocess.call(['sudo', 'vppctl', 'sr steer del l3', dest_prefix])
    subprocess.call(['sudo', 'vppctl', 'sr policy del bsid 101::101', dest_prefix])
    subprocess.call(['sudo', 'vppctl', 'sr', 'policy', 'add', 'bsid', '101::101', 'next', usid_stack, 'encap'])
    subprocess.call(['sudo', 'vppctl', 'sr', 'steer', 'l3', dest_prefix, 'via', 'bsid', '101::101'])
    
    logging.info('vppctl show ip fib %s', dest_prefix)
    subprocess.call(['sudo', 'vppctl', 'show', 'ip', 'fib', dest_prefix])
    
if __name__ == '__srv6_util__':
    srv6_util()