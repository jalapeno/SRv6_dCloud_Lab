import json
from arango import ArangoClient
from . import add_route

# Query DB for least utilized path parameters and return srv6 SID
def lu_calc(src_id, dst_id, dst, user, pw, dbname, intf, route):

    client = ArangoClient(hosts='http://198.18.1.101:30852')
    db = client.db(dbname, username=user, password=pw)
    cursor = db.aql.execute("""for v, e in outbound shortest_path """ + '"%s"' % src_id + """ \
        TO """ + '"%s"' % dst_id + """ sr_topology \
            OPTIONS { weightAttribute: 'percent_util_out' } filter e.mt_id != 2 \
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
            'source': src_id,
            'destination': dst_id,
            'sid': srv6_sid,
            'path': path
        }

    print("route_add parameters = sid: ", srv6_sid, "dest: ", dst, "intf: ", intf, "route type: ", route)
    route_add = add_route.add_linux_route(dst, srv6_sid, intf, route)
    pathobj = json.dumps(pathdict, indent=4)
    return(pathobj)


    
