import json
from arango import ArangoClient

username = "username"
password = "password"
database = "database"
source = "source"
destination = "destination"

f = open("src_dst.json")
sd = json.load(f)

user = sd[username]
pw = sd[password]
dbname = sd[database]
src = sd[source]
dst = sd[destination]

client = ArangoClient(hosts='http://52.11.224.254:30852')
#client = ArangoClient(hosts='http://10.200.99.7:30852')
db = client.db(dbname, username=user, password=pw)

if db.has_collection('sr_topology'):
    srt = db.collection('sr_topology')

srt.properties()
#util_key = "percent_util_out"
#router_id_key = "node"

# Get source node to begin graph traversal
aql = db.aql
cursor = db.aql.execute("""for u in unicast_prefix_v4 filter u.prefix == """  + '"%s"' % src +  """ return u.peer_ip """)
peer = [doc for doc in cursor]
print("peer ip: ", peer)
pr = peer[0]
aql = db.aql
cursor = db.aql.execute("""for s in sr_node filter s.router_id == """  + '"%s"' % pr +  """ return s._id """)
src_node = [doc for doc in cursor]
print("source node: ", src_node)

# Get destination prefix ID in edge collection
aql = db.aql
cursor = db.aql.execute("""for u in unicast_prefix_v4 \
    filter u.prefix == """  + '"%s"' % dst +  """ return { id: u._id, dest_peer: u.peer_ip } """)
dst_dict = [doc for doc in cursor]
#print(dst_dict)

id = "id"
dest_peer = "dest_peer"
dest_id = [a_dict[id] for a_dict in dst_dict]

s = src_node[0]
d = dst_dict[0]

aql = db.aql
cursor = db.aql.execute("""for v, e, p in 1..6 outbound """ + '"%s"' % s + """ \
        sr_topology OPTIONS {uniqueVertices: "path", bfs: true} \
            filter v._id == """ + '"%s"' % d[id] + """ \
                return { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, \
                    latency: sum(p.edges[*].latency), \
                        percent_util_out: avg(p.edges[*].percent_util_out)} """)

path = [doc for doc in cursor]
#print(path)
for index in range(len(path)):
    for key in path[index]:
        #print(key, ":", path[index][key])
        if key == "sid":
            #print("sid: ", path[index][key])
            sids = path[index][key]
            usid_block = 'fc00:0:'
            #print("sids: ", sids)
            for sid in list(sids):
                if sid == None:
                    sids.remove(sid)
            #print("sids: ", sids)
            usid = []
            for s in sids:
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
            #print("srv6 sid: ", srv6_sid)
            siddict = {}
            siddict['srv6_sid'] = srv6_sid
            path[index][key].append(siddict)

pathdict = path
    
errordict = {
    'statusCode': 200,
    'sid': 'Source and destination are reachable via the same router, no optimization available',
    'source': src,
    'destination': dst
}

if pr == d[dest_peer]:
    print(errordict)
else:
    pathobj = json.dumps(pathdict, indent=4)
    print(pathobj)
