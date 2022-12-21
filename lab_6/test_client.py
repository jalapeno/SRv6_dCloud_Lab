import argparse
import json
from rome import least_util, low_latency, data_sovereignty, get_paths, src_dst, lu, ll, ds

def main():
    parser = argparse.ArgumentParser(
        prog = 'Jalapeno client',
        description = 'takes command line input and calls path calculator functions',
        epilog = 'client.py -f <json file> -e <sr or srv6> -s <ll, lu, or ds>')
    parser.add_argument("-e", help="encapsulation type <sr> <srv6>", default="a string")
    parser.add_argument("-f", help="json file with src, dst, parameters", default="a string") 
    parser.add_argument("-s", help="requested network service: ll = low_latency, lu = least_utilized, ds = data_sovereignty, gp = get_paths)", default="a string")
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
    country = "country"

    f = open(file)
    sd = json.load(f)

    user = sd[username]
    pw = sd[password]
    dbname = sd[database]
    src = sd[source]
    dst = sd[destination]
    intf = sd[interface]
    ctr = sd[country]

    sd_tuple = src_dst.get_src_dst(src, dst, user, pw, dbname)
    #print(sd)
    st = sd_tuple[0]
    dt = sd_tuple[1]
    if encap == "srv6":
        if service == "lu":
            srv6_lu = lu.lu_calc(st, dt, user, pw, dbname, intf)
        if service == "ll":
            srv6_ll = ll.ll_calc(st, dt, user, pw, dbname, intf)  
        if service == "ds":
            srv6_ds = ds.ds_calc(st, dt, user, pw, dbname, ctr, intf)
        if service == "gp":
            srv6_gp = get_paths.gp_calc(st, dt, user, pw, dbname)
        
        else:
            print(""" 
            Please specify a service (ll, lu, ds, vpn)
            
            """)

if __name__ == '__main__':
    main()