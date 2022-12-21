import json
import sys
import subprocess
from arango import ArangoClient
from . import add_route

# Query DB for least utilized path parameters and return srv6 SID
def lu_calc(src, dst, user, pw, dbname, intf):

    client = ArangoClient(hosts='http://198.18.1.101:30852')
    db = client.db(dbname, username=user, password=pw)

    aql = db.aql
    cursor = db.aql.execute("""for u in unicast_prefix_v4 filter u.prefix == """  + '"%s"' % src +  """ \
        return { id: u._id, src_peer: u.peer_ip } """)
    src_dict = [doc for doc in cursor]
    #print(src_dict)

    # Get destination prefix ID to end graph traversal
    aql = db.aql
    cursor = db.aql.execute("""for u in unicast_prefix_v4 filter u.prefix == """  + '"%s"' % dst +  """ \
        return { id: u._id, dst_peer: u.peer_ip } """)
    dst_dict = [doc for doc in cursor]
    #print(dst_dict)

    id = "id"
    src_peer = "src_peer"
    dst_peer = "dst_peer"

    s = src_dict[0]
    d = dst_dict[0]

    if s[src_peer] == d[dst_peer]:
        print(""" 
        Source and destination are reachable via the same router, no optimization available
        
        """)
    else:
        aql = db.aql
        cursor = db.aql.execute("""for v, e in outbound shortest_path """ + '"%s"' % s[id] + """ TO """ + '"%s"' % d[id] + \
                """ sr_topology OPTIONS { weightAttribute: 'percent_util_out' } filter e.mt_id != 2 \
                    return { node: v._key, name: v.name, sid: e.srv6_sid, util: e.percent_util_out } """)
        path = [doc for doc in cursor]

        sid = 'sid'
        usid_block = 'fc00:0:'

        locators = [a_dict[sid] for a_dict in path]
        #print(sids)

        for sid in list(locators):
            if sid == None:
                locators.remove(sid)
        print("locators: ", locators)

        usid = []
        for s in locators:
            if s != None and usid_block in s:
                usid_list = s.split(usid_block)
                sid = usid_list[1]
                usid_int = sid.split(':')
                u = int(usid_int[0])
                usid.append(u)

        ipv6_separator = ":"

        sidlist = ""
        for word in usid:
            sidlist += str(word) + ":"
        #print(sidlist)

        srv6_sid = usid_block + sidlist + ipv6_separator
        print("srv6 sid: ", srv6_sid)

        pathdict = {
                'statusCode': 200,
                'source': src,
                'destination': dst,
                'sid': srv6_sid,
                'path': path
            }

        pathobj = json.dumps(pathdict, indent=4)
        with open('log/least_util_log.json', 'w') as f:
            sys.stdout = f 
            print(pathobj)

        route = add_route.add_linux_route(dst, srv6_sid, intf)
        print("adding linux route: ", route)
        
