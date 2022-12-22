import argparse
import json
from netservice import src_dst, lu, ll, ds, gp

def main():
    parser = argparse.ArgumentParser(
        prog = 'Jalapeno client',
        description = 'takes command line input and calls path calculator functions',
        epilog = 'client.py -f <json file> -e <sr or srv6> -s <sr, lu, ds, or gp> ')
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

    sd_tuple = src_dst.get_src_dst(src, dst, user, pw, dbname)
    #print(sd)
    st = sd_tuple[0]
    dt = sd_tuple[1]
    if encap == "srv6":
        if service == "lu":
            srv6_lu = lu.lu_calc(st, dt, user, pw, dbname, intf, route)
        if service == "ll":
            srv6_ll = ll.ll_calc(st, dt, user, pw, dbname, intf, route)  
        if service == "ds":
            srv6_ds = ds.ds_calc(st, dt, user, pw, dbname, ctr, intf, route)
        if service == "gp":
            srv6_gp = gp.gp_calc(st, dt, user, pw, dbname)
        
        else:
            print(""" 
            Please specify a service: sr, lu, ll, ds, or vpn
            """)
    if encap == "sr":
        if service == "lu":
            sr_lu = lu.lu_calc(st, dt, user, pw, dbname, intf, route)
        if service == "sr":
            sr_ll = ll.ll_calc(st, dt, user, pw, dbname, intf, route)  
        if service == "ds":
            sr_ds = ds.ds_calc(st, dt, user, pw, dbname, ctr, intf, route)
        if service == "gp":
            sr_gp = gp.sr_gp_calc(st, dt, user, pw, dbname)
        
        else:
            print(""" 
            Please specify a service: sr, lu, ll, ds, or vpn
            """)
    # else:
    #     print(""" 
    #     Please specify an encapsulation type (sr, srv6)
    #     """)

if __name__ == '__main__':
    main()