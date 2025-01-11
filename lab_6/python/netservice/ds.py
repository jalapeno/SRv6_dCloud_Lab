import json
from arango import ArangoClient
from . import add_route, local_sid

### SRv6 Data Sovereignty
# Query DB for a path that avoids a given country and return srv6 and sr sid info
def ds_calc(src_id, dst_id, dst, user, pw, dbname, ctr, intf, dataplane, encap):
    #print("dst: ", dst)
    client = ArangoClient(hosts='http://198.18.128.101:30852')
    db = client.db(dbname, username=user, password=pw)
    cursor = db.aql.execute("""for p in outbound k_shortest_paths \
        """ + '"%s"' % src_id + """ to """ + '"%s"' % dst_id + """ ipv4_graph \
            options {uniqueVertices: "path", bfs: true} \
            filter p.edges[*].country_codes !like "%"""+'%s' % ctr +"""%" limit 1 \
                return { path: p.vertices[*].name, sid: p.vertices[*].sids[*].srv6_sid, \
                    countries_traversed: p.edges[*].country_codes[*], latency: sum(p.edges[*].latency), \
                        percent_util_out: avg(p.edges[*].percent_util_out)} """)

    path = [doc for doc in cursor]
    print("path: ", path)

    pdict = path[0]

    ### SRv6 SID processing
    locators = pdict['sid']
    usid_block = 'fc00:0:'

    for sid in list(locators):
        if sid == None:
            locators.remove(sid)
    #print("locators: ", locators)

    loc = [ele for ele in locators if ele != []]
    locatorlist=[x for n in (loc) for x in n]
    locatorlist.pop(0) # remove first entry as its the ingress SRv6 node
    print()
    print("locator list for data sovereignty path: ", locatorlist)
    usid = []
    for s in locatorlist:
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

    ### From here we're going to get the end.dt localsid and add it to the uSID dest
    locator = locatorlist[-1]
    print("egress node locator: ", locator)
    localsid = local_sid.localsid(user, pw, dbname,locator, usid_block)
    
    usd = locator.replace(usid_block, '')

    ### this is from original
    srv6_sid = usid_block + sidlist + ipv6_separator

    ### replace usd sid with end.dt 
    newsid = srv6_sid.replace(usd, localsid)

    ### Return to original code
    print("srv6 sid: ", newsid)

    ### from here on replace "srv6_sid" variable with "newsid"


    siddict = {}
    siddict['srv6_sid'] = newsid
    path.append(siddict)

    ### SR MPLS processing
    prefix_sid = 'prefix_sid'
    # prefix_sid = pdict['prefix_sid']
    # for sid in list(prefix_sid):
    #     if sid == None:
    #         prefix_sid.remove(sid)
    # print("prefix_sids: ", prefix_sid)

    pathdict = {
            'statusCode': 200,
            'source': src_id,
            'destination': dst_id,
            'sid': newsid,
            'path': path
        }    
    #print("route_add parameters = sid: ", srv6_sid, "sr_label_stack: ", prefix_sid, "dest: ", dst, "intf: ", intf, "dataplane: ", dataplane)
    if dataplane == "linux":
        route_add = add_route.add_linux_route(dst, newsid, prefix_sid, intf, encap)
    if dataplane == "vpp":
        route_add = add_route.add_vpp_route(dst, newsid, prefix_sid, encap)
    pathobj = json.dumps(pathdict, indent=4)
    return(pathobj)


