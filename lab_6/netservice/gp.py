import json
import sys
from arango import ArangoClient

# Query DB for least utilized path parameters and return srv6 SID
def gp_calc(src, dst, user, pw, dbname):

    client = ArangoClient(hosts='http://198.18.1.101:30852')
    db = client.db(dbname, username=user, password=pw)

    aql = db.aql
    cursor = db.aql.execute("""for v, e, p in 1..6 outbound """ + '"%s"' % src + """ \
            sr_topology OPTIONS {uniqueVertices: "path", bfs: true} \
                filter v._id == """ + '"%s"' % dst + """ \
                    return { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, \
                        latency: sum(p.edges[*].latency), \
                            percent_util_out: avg(p.edges[*].percent_util_out)} """)

    path = [doc for doc in cursor]
    for index in range(len(path)):
        for key in path[index]:
            #print(key, ":", path[index][key])
            if key == "sid":
                #print("sid: ", path[index][key])
                locators = path[index][key]
                usid_block = 'fc00:0:'
                #print("locators: ", locators)
                for sid in list(locators):
                    if sid == None:
                        locators.remove(sid)
                print("locators: ", locators)
                usid = []
                for s in locators:
                    if s != None and usid_block in s:
                        usid_list = s.split(usid_block)
                        #print(usid_list)
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
                siddict = {}
                siddict['srv6_sid'] = srv6_sid
                path[index][key].append(siddict)

    pathdict = path
        
    pathdict = {
            'statusCode': 200,
            'source': src,
            'destination': dst,
            'sid': srv6_sid,
            'path': path
        }

    pathobj = json.dumps(pathdict, indent=4)
    with open('netservice/log/srv6_get_paths.json', 'w') as f:
        sys.stdout = f 
        print(pathobj)

def sr_gp_calc(src, dst, user, pw, dbname):

    client = ArangoClient(hosts='http://198.18.1.101:30852')
    db = client.db(dbname, username=user, password=pw)

    aql = db.aql
    cursor = db.aql.execute("""for v, e, p in 1..6 outbound """ + '"%s"' % src + """ \
            sr_topology OPTIONS {uniqueVertices: "path", bfs: true} \
                filter v._id == """ + '"%s"' % dst + """ \
                    return { path: p.edges[*].remote_node_name, sid: p.vertices[*].prefix_sid, \
                        latency: sum(p.edges[*].latency), \
                            percent_util_out: avg(p.edges[*].percent_util_out)} """)

    path = [doc for doc in cursor]
    for index in range(len(path)):
        for key in path[index]:
            print(key, ":", path[index][key])
            if key == "sid":
                print("sid: ", path[index][key])
                prefix_sids = path[index][key]
                usid_block = 'fc00:0:'
                #print("prefix_sids: ", prefix_sids)
                for sid in list(prefix_sids):
                    if sid == None:
                        prefix_sids.remove(sid)
                print("prefix sids: ", prefix_sids)

    pathdict = path
        
    pathdict = {
            'statusCode': 200,
            'source': src,
            'destination': dst,
            'sid': prefix_sids,
            'path': path
        }

    pathobj = json.dumps(pathdict, indent=4)
    with open('netservice/log/sr_get_paths.json', 'w') as f:
        sys.stdout = f 
        print(pathobj)