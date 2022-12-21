import json
from arango import ArangoClient
from math import ceil
import sys
from . import add_route

# Query DB for low latency path parameters and return srv6 SID
def ll_calc(src, dst, user, pw, dbname, intf):

    client = ArangoClient(hosts='http://198.18.1.101:30852')
    db = client.db(dbname, username=user, password=pw)
    print("source id: ", src)
    print("dest id: ", dst)
    aql = db.aql
    cursor = db.aql.execute("""for v, e in outbound shortest_path """ + '"%s"' % src +  """ \
        TO """ + '"%s"' % dst +  """ sr_topology \
            OPTIONS {weightAttribute: 'latency' } \
                return  { node: v._key, name: v.name, sid: e.srv6_sid, latency: e.latency } """)
    path = [doc for doc in cursor]
    #print("path: ", path)
    hopcount = len(path)
    #print("hops: ", hopcount)
    pq = ceil((hopcount/2)-1)
    #print(pq)
    pq_node = (path[pq])
    #print("pqnode: ", pq_node)
    sid = 'sid'
    usid_block = 'fc00:0:'

    sids = [a_dict[sid] for a_dict in path]
    print(sids)

    for sid in list(sids):
        if sid == None:
            sids.remove(sid)
    print(sids)

    usid = []
    for s in sids:
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
    with open('log/low_latency_log.json', 'w') as f:
        sys.stdout = f 
        print(pathobj)

    route = add_route.add_linux_route(dst, srv6_sid, intf)
    print("adding linux route: ", route)
