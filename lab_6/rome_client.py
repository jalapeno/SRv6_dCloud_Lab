#from pkg import sr_latency, srv6_latency, srv6_util, ext_latency
import argparse
import json
from rome import get_least_util, least_util, get_all_paths, get_low_latency, data_sovereignty, get_v4_topology

def main():
    parser = argparse.ArgumentParser(description='rome client')#,
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        # epilog=('''\
        #  example: python3 rome_client.py -s low_latency -e srv6
        #  '''))
    # parser.add_argument("-d", help="destination prefix <prefix/len>", default="a string")
    # parser.add_argument("-s", help="path SLA service <low_latency> <least_utilized> <data_sovereignty", default="a string")
    parser.add_argument("-e", help="encapsulation type <sr> <srv6>", default="a string")
    parser.add_argument("-f", help="json file with src, dst, parameters", default="a string")
    args = parser.parse_args()

    # dest_prefix = args.d
    # service = args.s
    encap = args.e
    file = args.f

    f = json.load(file)
    f_dict = [doc for doc in f]
    print(f_dict)
    username = "username"
    password = "password"
    database = "database"
    source = "source"
    destination = "destination"


    # if encap == "srv6":
    #     if service == "least_utilized":
    #         #srv6_lu = get_least_util(prefix_split[0], dest_prefix)
    #         srv6_lu = least_util.lu_logic(prefix_split[0], dest_prefix)
    #     if service == "low_latency":
    #         srv6_ll = get_low_latency(prefix_split[0], dest_prefix)
    #     if service == "data_sovereignty":
    #         srv6_ds = data_sovereignty(prefix_split[0], dest_prefix)
    #     else:
    #         print("please specify a service. Example: python3 rome_client.py -s low_latency -e srv6")
    
    # if encap == "sr":
    #     if service == "least_utilized":
    #         srv6_lu = get_least_util(prefix_split[0], dest_prefix)
    #     if service == "low_latency":
    #         srv6_ll = get_low_latency(prefix_split[0], dest_prefix)
    #     if service == "data_sovereignty":
    #         srv6_ds = data_sovereignty(prefix_split[0], dest_prefix)
    #     else:
    #         print("please specify a service. Example: python3 rome_client.py -s low_latency -e srv6")
    # else:
    #     print("please specify an encap and service. Example: python3 rome_client.py -s low_latency -e srv6")
    # return 

if __name__ == '__main__':
    main()