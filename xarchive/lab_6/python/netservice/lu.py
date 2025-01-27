import json
from arango import ArangoClient
from . import add_route, local_sid

# Query DB for least utilized path parameters and return srv6 and sr sid info
def lu_calc(src_id, dst_id, dst, user, pw, dbname, intf, dataplane, encap):

    #print("src, dst: ", src_id, dst_id)
    
    client = ArangoClient(hosts='http://198.18.128.101:30852')
    db = client.db(dbname, username=user, password=pw)
    cursor = db.aql.execute("""for v, e in outbound shortest_path """ + '"%s"' % src_id + """ \
        to """ + '"%s"' % dst_id + """ ipv4_graph \
            options { weightAttribute: 'percent_util_out' } filter e.mt_id != 2 \
                return { node: v._key, name: v.name, sid: v.sids[*].srv6_sid, util: e.percent_util_out } """)
    path = [doc for doc in cursor]

    prefix_sid = 'prefix_sid'
    # prefix_sid = [a_dict[prefix_sid] for a_dict in path]
    # for ps in list(prefix_sid):
    #     if ps == None:
    #         prefix_sid.remove(ps)
    # print("prefix_sids: ", prefix_sid)

    sid = 'sid'
    usid_block = 'fc00:0:'
    locators = [a_dict[sid] for a_dict in path]
    for sid in list(locators):
        if sid == None:
            locators.remove(sid)
    #print("locators: ", locators)
    loc = [ele for ele in locators if ele != []]
    locatorlist=[x for n in (loc) for x in n]
    locatorlist.pop(0) # remove first entry as its the ingress SRv6 node
    print("locator list for least utilized path: ", locatorlist)
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
    #print(sidlist)

    ### From here we're going to get the end.dt localsid and add it to the uSID dest
    locator = locatorlist[-1]
    print("egress node locator: ", locator)
    localsid = local_sid.localsid(user, pw, dbname, locator, usid_block)
    
    usd = locator.replace(usid_block, '')

    ### this is from original
    srv6_sid = usid_block + sidlist + ipv6_separator
    #print("original: ", srv6_sid)

    ### replace usd sid with end.dt 
    newsid = srv6_sid.replace(usd, localsid)
    print("srv6 sid: ", newsid)

    ### Return to original code
    #print("srv6 sid: ", srv6_sid)

    ### from here on replace "srv6_sid" variable with "newsid"
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


    
