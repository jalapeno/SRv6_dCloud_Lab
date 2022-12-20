import json
import sys
import subprocess
from arango import ArangoClient

def lu_logic():

    username = "username"
    password = "password"
    database = "database"
    source = "source"
    destination = "destination"

    f = open("rome_src_dst.json")
    sd = json.load(f)

    user = sd[username]
    pw = sd[password]
    dbname = sd[database]
    src = sd[source]
    dst = sd[destination]

    client = ArangoClient(hosts='http://198.18.1.101:30852')
    db = client.db(dbname, username=user, password=pw)

    if db.has_collection('sr_topology'):
        srt = db.collection('sr_topology')

    srt.properties()

    # Get source node to begin graph traversal
    aql = db.aql
    cursor = db.aql.execute("""for u in unicast_prefix_v4 filter u.prefix == """  + '"%s"' % src +  """ \
        && u.base_attrs.local_pref != Null return u.peer_ip """)
    peer = [doc for doc in cursor]
    #print("peer ip: ", peer)
    pr = peer[0]
    aql = db.aql
    cursor = db.aql.execute("""for s in sr_node filter s.router_id == """  + '"%s"' % pr +  """ return s._id """)
    src_node = [doc for doc in cursor]
    #print("source node: ", src_node)

    # Get destination prefix ID in edge collection
    aql = db.aql
    cursor = db.aql.execute("""for u in unicast_prefix_v4 filter u.prefix == """  + '"%s"' % dst +  """ \
        return { id: u._id, dest_peer: u.peer_ip } """)
    dst_dict = [doc for doc in cursor]
    #print(dst_dict)

    id = "id"
    dest_peer = "dest_peer"
    dest_id = [a_dict[id] for a_dict in dst_dict]


    s = src_node[0]
    d = dst_dict[0]

    aql = db.aql
    cursor = db.aql.execute("""for v, e in outbound shortest_path """ + '"%s"' % s + """ TO """ + '"%s"' % d[id] + \
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
    if pr == d[dest_peer]:
        print(""" 
        Source and destination are reachable via the same router, no optimization available
        
        """)
    else:
        pathdict = {
                'statusCode': 200,
                'source': src,
                'destination': dst,
                'sid': srv6_sid,
                'path': path
            }

        pathobj = json.dumps(pathdict, indent=4)
        with open('log/get_least_util_log.json', 'w') as f:
            sys.stdout = f 
            print(pathobj)

        subprocess.call(['sudo', 'ip', 'route', 'add', dst, 'encap', 'seg6', 'mode', 'encap', 'segs', srv6_sid, 'dev', 'ens192'])
        # sudo ip -6 route add 10.0.0.1/32 encap seg6 mode segs fc00:0:2:3:4:7:: dev ens192
        subprocess.call(['ip', 'route'])
        
