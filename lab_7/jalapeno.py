import argparse
import json
import sys
from netservice import src_dst, lu, ll, ds, gp

### Jalapeno/SDN client ###

def main():
    # Handle cli options passed in
    parser = argparse.ArgumentParser(
        prog = 'Jalapeno client',
        description = 'takes command line input and calls path calculator functions',
        epilog = 'jalapeno.py -f <json file> -e <sr or srv6> -s <ll, lu, ds, or gp> ')
    parser.add_argument("-e", help="encapsulation type <sr> <srv6>")
    parser.add_argument("-f", help="json file with src, dst, parameters")  
    parser.add_argument("-s", help="requested network service: ll = low_latency, lu = least_utilized, ds = data_sovereignty, gp = get_paths)")
    args = parser.parse_args()

    encap = args.e
    file = args.f
    service = args.s

    # Check that the required input arguments were passed in
    if not encap or not file or not service:
        print("Required input elements encapsulation type, input file, and/or service type were not entered")
        print("jalapeno.py -f <json file> -e <sr | srv6> -s <ll, lu, ds, or gp>")
        exit()


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
    #print(sd_tuple)
    src_id = sd_tuple[0]
    dst_id = sd_tuple[1]
    if service == "ds":
        print("Data Sovereignty Service")
        srv6_ds = ds.ds_calc(src_id, dst_id, dst, user, pw, dbname, ctr, intf, dataplane, encap)
        with open('log/data_sovereignty.json', 'a') as f:
            sys.stdout = f 
            print(srv6_ds)
    if service == "gp":
        print("Get All Paths Service")
        gp_srv = gp.gp_calc(src_id, dst_id, user, pw, dbname)  
        with open('log/get_paths.json', 'a') as f:
            sys.stdout = f 
            print(gp_srv)                 
    if service == "ll":
        print("Low Latency Service")
        srv6_ll = ll.ll_calc(src_id, dst_id, dst, user, pw, dbname, intf, dataplane, encap) 
        with open('log/low_latency.json', 'a') as f:
            sys.stdout = f 
            print(srv6_ll) 
    if service == "lu":
        print("Least Utilized Service")
        srv6_lu = lu.lu_calc(src_id, dst_id, dst, user, pw, dbname, intf, dataplane, encap)
        with open('log/least_util.json', 'a') as f:
            sys.stdout = f 
            print(srv6_lu)

if __name__ == '__main__':
    main()