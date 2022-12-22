import argparse
import json
import sys
from netservice import src_dst, lu, ll, ds, gp

def main():
    parser = argparse.ArgumentParser(
        prog = 'Jalapeno client',
        description = 'takes command line input and calls path calculator functions',
        epilog = 'client.py -f <json file> -e <sr or srv6> -s <ll, lu, ds, or gp> ')
    parser.add_argument("-e", help="encapsulation type <sr> <srv6>", default="a string")
    parser.add_argument("-f", help="json file with src, dst, parameters", default="a string")  
    parser.add_argument("-s", help="requested network service: sr = low_latency, lu = least_utilized, ds = data_sovereignty, gp = get_paths)", default="a string")
    args = parser.parse_args()

    encap = args.e
    file = args.f
    service = args.s

    username = "username"
    password = "password"
    database = "database"
    source = "source"
    destination = "destination"
    interface = "interface"
    route = "route"
    country = "country"

    f = open(file)
    sd = json.load(f)

    user = sd[username]
    pw = sd[password]
    dbname = sd[database]
    src = sd[source]
    dst = sd[destination]
    intf = sd[interface]
    route = sd[route]
    ctr = sd[country]

    srcpfxsplit = list(src.split('/'))
    srcprefix = srcpfxsplit[0]
    dstpfxsplit = list(dst.split('/'))
    dstprefix = dstpfxsplit[0]

    sd_tuple = src_dst.get_src_dst(srcprefix, dstprefix, user, pw, dbname)
    print(sd_tuple)
    src_id = sd_tuple[0]
    dst_id = sd_tuple[1]
    if encap == "srv6":
        if service == "ds":
            srv6_ds = ds.ds_calc(src_id, dst_id, dst, user, pw, dbname, ctr, intf, route)
        with open('netservice/log/srv6_data_sovereignty.json', 'w') as f:
            sys.stdout = f 
            print(srv6_ds)

        if service == "gp":
            srv6_gp = gp.gp_calc(src_id, dst_id, user, pw, dbname)            
            
        if service == "ll":
            srv6_ll = ll.ll_calc(src_id, dst_id, dst, user, pw, dbname, intf, route)  

        if service == "lu":
            srv6_lu = lu.lu_calc(src_id, dst_id, dst, user, pw, dbname, intf, route)

        
        # else:
        #     print(""" 
        #     Please specify a service: ll, lu, ds, or gp
        #     """)
    if encap == "sr":
        if service == "lu":
            sr_lu = lu.lu_calc(src_id, dst_id, dst, user, pw, dbname, intf, route)
        if service == "ll":
            sr_ll = ll.ll_calc(src_id, dst_id, dst, user, pw, dbname, intf, route)  
        if service == "ds":
            sr_ds = ds.ds_calc(src_id, dst_id, dst, user, pw, dbname, ctr, intf, route)
        if service == "gp":
            sr_gp = gp.sr_gp_calc(src_id, dst_id, dst, user, pw, dbname)
        
        else:
            print(""" 
            Please specify a service: ll, lu, ds, or gp
            """)
    # else:
    #     print(""" 
    #     Please specify an encapsulation type (sr, srv6)
    #     """)

if __name__ == '__main__':
    main()