import json
from arango import ArangoClient
from . import add_route

### SRv6 Data Sovereignty
# Query DB for a path that avoids a given country and return srv6 SID
def srv6_ds_calc(src_id, dst_id, dst, user, pw, dbname, ctr, intf, dataplane):
    print("dst: ", dst)
    client = ArangoClient(hosts='http://198.18.1.101:30852')
    db = client.db(dbname, username=user, password=pw)
    cursor = db.aql.execute("""for p in outbound k_shortest_paths \
        """ + '"%s"' % src_id + """ TO """ + '"%s"' % dst_id + """ sr_topology \
            options {uniqueVertices: "path", bfs: true} \
            filter p.edges[*].country_codes !like "%"""+'%s' % ctr +"""%" limit 1 \
                return { path: p.edges[*].remote_node_name, sid: p.edges[*].srv6_sid, \
                    countries_traversed: p.edges[*].country_codes[*], latency: sum(p.edges[*].latency), \
                        percent_util_out: avg(p.edges[*].percent_util_out)} """)

    path = [doc for doc in cursor]
    print("path: ", path)

    pdict = path[0]
    locators = pdict['sid']
    usid_block = 'fc00:0:'

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

    srv6_sid = usid_block + sidlist + ipv6_separator
    print("srv6 sid: ", srv6_sid)
    #print("path: ", path)

    siddict = {}
    siddict['srv6_sid'] = srv6_sid
    path.append(siddict)

    pathdict = {
            'statusCode': 200,
            'source': src_id,
            'destination': dst_id,
            'sid': srv6_sid,
            'path': path
        }
        
    print("route_add parameters = sid: ", srv6_sid, "dest: ", dst, "intf: ", intf, "dataplane: ", dataplane)
    if dataplane == "linux":
        route_add = add_route.add_linux_route(dst, srv6_sid, intf)
    if dataplane == "vpp":
        route_add = add_route.add_vpp_route(dst, srv6_sid)
    pathobj = json.dumps(pathdict, indent=4)
    return(pathobj)


### SR Data Sovereignty
# Query DB for a path that avoids a given country and return SR label stack
def sr_ds_calc(src_id, dst_id, dst, user, pw, dbname, ctr, intf, dataplane):
    print("dst: ", dst)
    client = ArangoClient(hosts='http://198.18.1.101:30852')
    db = client.db(dbname, username=user, password=pw)
    cursor = db.aql.execute("""for p in outbound k_shortest_paths \
        """ + '"%s"' % src_id + """ TO """ + '"%s"' % dst_id + """ sr_topology \
            options {uniqueVertices: "path", bfs: true} \
            filter p.edges[*].country_codes !like "%"""+'%s' % ctr +"""%" limit 1 \
                return { path: p.edges[*].remote_node_name, sid: p.edges[*].prefix_attr_tlvs.ls_prefix_sid[0], \
                    countries_traversed: p.edges[*].country_codes[*], latency: sum(p.edges[*].latency), \
                        percent_util_out: avg(p.edges[*].percent_util_out)} """)

    path = [doc for doc in cursor]
    #print("path: ", path)
    pathdict = path[0]

    #print(pathdict['sid'])
    print(pathdict)
    print(type(pathdict))

    print()

    pathobj = json.dumps(path, indent=4)
    #print(pathobj)
    # q = [item[0] for item in pathobj]
    # print(q)
    # r = q[0]
    # print(r)
 

    # pathdict = {
    #         'statusCode': 200,
    #         'source': src_id,
    #         'destination': dst_id,
    #         'sid': srv6_sid,
    #         'path': path
    #     }
        
    # print("route_add parameters = sid: ", srv6_sid, "dest: ", dst, "intf: ", intf, "dataplane: ", dataplane)
    # if dataplane == "linux":
    #     route_add = add_route.add_linux_route(dst, srv6_sid, intf)
    # if dataplane == "vpp":
    #     route_add = add_route.add_vpp_route(dst, srv6_sid)
    # pathobj = json.dumps(pathdict, indent=4)
    # return(pathobj)

