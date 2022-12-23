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
    dataplane = "dataplane"
    country = "country"

    f = open(file)
    sd = json.load(f)

    user = sd[username]
    pw = sd[password]
    dbname = sd[database]
    src = sd[source]
    dst = sd[destination]
    intf = sd[interface]
    dataplane = sd[dataplane]
    ctr = sd[country]

    srcpfxsplit = list(src.split('/'))
    srcprefix = srcpfxsplit[0]
    dstpfxsplit = list(dst.split('/'))
    dstprefix = dstpfxsplit[0]

    sd_tuple = src_dst.get_src_dst(srcprefix, dstprefix, user, pw, dbname)
    print(sd_tuple)
    src_id = sd_tuple[0]
    dst_id = sd_tuple[1]
    # if encap == "srv6":
    if service == "ds":
        print("invoke data sovereignty service")
        srv6_ds = ds.ds_calc(src_id, dst_id, dst, user, pw, dbname, ctr, intf, dataplane)
        with open('netservice/log/data_sovereignty.json', 'w') as f:
            sys.stdout = f 
            print(srv6_ds)
    if service == "gp":
        print("invoke get paths service")
        srv6_gp = gp.gp_calc(src_id, dst_id, user, pw, dbname)  
        with open('netservice/log/get_paths.json', 'w') as f:
            sys.stdout = f 
            print(srv6_gp)                 
    if service == "ll":
        print("invoke low latency service")
        srv6_ll = ll.ll_calc(src_id, dst_id, dst, user, pw, dbname, intf, dataplane) 
        with open('netservice/log/low_latency.json', 'w') as f:
            sys.stdout = f 
            print(srv6_ll) 
    if service == "lu":
        print("invoke least utilized service")
        srv6_lu = lu.lu_calc(src_id, dst_id, dst, user, pw, dbname, intf, dataplane)
        with open('netservice/log/least_util.json', 'w') as f:
            sys.stdout = f 
            print(srv6_lu)
        
    # if encap == "sr":
    #     if service == "ds":
    #         sr_ds = ds.ds_calc(src_id, dst_id, dst, user, pw, dbname, ctr, intf, dataplane)
    #         with open('netservice/log/data_sovereignty.json', 'w') as f:
    #             sys.stdout = f 
    #             print(sr_ds) 
    #     if service == "gp":
    #         print("invoke get paths service")
    #         sr_gp = gp.gp_calc(src_id, dst_id, user, pw, dbname)
    #         with open('netservice/log/get_paths.json', 'w') as f:
    #             sys.stdout = f 
    #             print(sr_gp) 
    #     if service == "ll":
    #         sr_ll = ll.ll_calc(src_id, dst_id, dst, user, pw, dbname, intf, dataplane) 
    #         with open('netservice/log/low_latency.json', 'w') as f:
    #             sys.stdout = f 
    #             print(sr_ll)  
    #     if service == "lu":
    #         sr_lu = lu.lu_calc(src_id, dst_id, dst, user, pw, dbname, intf, dataplane)
    #         with open('netservice/log/least_utilized.json', 'w') as f:
    #             sys.stdout = f 
    #             print(sr_lu) 
        
    # else:
    #     print(""" 
    #     Please specify an encapsulation type (sr, srv6)
    #     """)

if __name__ == '__main__':
    main()