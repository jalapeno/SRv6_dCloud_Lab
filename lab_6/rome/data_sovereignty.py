import json
from arango import ArangoClient

username = "username"
password = "password"
database = "database"
source = "source"
destination = "destination"
country = "country"

f = open("src_dst.json")
sd = json.load(f)

user = sd[username]
pw = sd[password]
dbname = sd[database]
src = sd[source]
dst = sd[destination]
ctr = sd[country]

print(src, dst, ctr)

client = ArangoClient(hosts='http://52.11.224.254:30852')
#client = ArangoClient(hosts='http://10.200.99.7:30852')
db = client.db(dbname, username=user, password=pw)

if db.has_collection('sr_topology'):
    srt = db.collection('sr_topology')

srt.properties()

# Get source node to begin graph traversal
aql = db.aql
cursor = db.aql.execute("""for u in unicast_prefix_v4 filter u.prefix == """  + '"%s"' % src +  """ \
    && u.base_attrs.local_pref != Null return u.peer_ip """)
src_peer = [doc for doc in cursor]
print("source peer ip: ", src_peer)
pr = src_peer[0]
aql = db.aql
cursor = db.aql.execute("""for s in sr_node filter s.router_id == """  + '"%s"' % pr +  """ return s._id """)
src_node = [doc for doc in cursor]
print("source igp node: ", src_node)

# Get destination prefix ID in edge collection
aql = db.aql
cursor = db.aql.execute("""for u in unicast_prefix_v4 filter u.prefix == """  + '"%s"' % dst +  """ \
    && u.base_attrs.local_pref == Null return { id: u._id, dest_peer: u.peer_ip } """)
dst_dict = [doc for doc in cursor]
print("dest dict: ", dst_dict)

id = "id"
dest_peer = "dest_peer"
dest_id = [a_dict[id] for a_dict in dst_dict]

s = src_node[0]
d = dst_dict[0]
print("d: ", d)

aql = db.aql
cursor = db.aql.execute("""for p in outbound k_shortest_paths \
    """ + '"%s"' % s + """ TO """ + '"%s"' % d[id] + """ sr_topology \
        options {uniqueVertices: "path", bfs: true} \
        filter p.edges[*].country_codes !like "%"""+'%s' % ctr +"""%" limit 1 \
            return { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, \
                countries_traversed: p.edges[*].country_codes[*], latency: sum(p.edges[*].latency), \
                    percent_util_out: avg(p.edges[*].percent_util_out)} """)

path = [doc for doc in cursor]
print("path: ", path)


id = "id"
dest_peer = "dest_peer"
dest_id = [a_dict[id] for a_dict in dst_dict]

s = src_node[0]
d = dst_dict[0]
print("d: ", d)

aql = db.aql
cursor = db.aql.execute("""for p in outbound k_shortest_paths \
    """ + '"%s"' % s + """ TO """ + '"%s"' % d[id] + """ sr_topology \
        options {uniqueVertices: "path", bfs: true} \
        filter p.edges[*].country_codes !like "%"""+'%s' % ctr +"""%" limit 1 \
            return { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, \
                countries_traversed: p.edges[*].country_codes[*], latency: sum(p.edges[*].latency), \
                    percent_util_out: avg(p.edges[*].percent_util_out)} """)

path = [doc for doc in cursor]
print("path: ", path)

pdict = path[0]
sids = pdict['sid']
usid_block = 'fc00:0:'
print("sids: ", sids)

for sid in list(sids):
    if sid == None:
        sids.remove(sid)

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

srv6_sid = usid_block + sidlist + ipv6_separator
print("srv6 sid: ", srv6_sid)
print("path: ", path)

siddict = {}
siddict['srv6_sid'] = srv6_sid
path.append(siddict)

if pr == d[dest_peer]:
    print(""" 
    Source and destination are reachable via the same router, no optimization available
    
    """)
else:
    pathdict = path
    pathobj = json.dumps(pathdict, indent=4)
    print(pathobj)
