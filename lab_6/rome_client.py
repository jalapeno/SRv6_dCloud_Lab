#from pkg import sr_latency, srv6_latency, srv6_util, ext_latency
import argparse

def main():
    parser = argparse.ArgumentParser(description='jalapeno client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=('''\
         example: python3 rome_client.py -s low_latency -e srv6 -f src_dst.json
         '''))
    parser.add_argument("-d", help="destination prefix <prefix/len>", default="a string")
    parser.add_argument("-s", help="path SLA service <low_latency> <least_utilized> <data_sovereignty", default="a string")
    parser.add_argument("-e", help="encapsulation type <sr> <srv6>", default="a string")
    parser.add_argument("-f", help="json file <src_dst.json> ", default="a string")
    args = parser.parse_args()
    #print(args.d, args.s)

    dest_prefix = args.d
    service = args.s
    encap = args.e
    file = args.f

    prefix_split = list(dest_prefix.split('/'))
    #print("dest prefix: ", dest_prefix)
    #print("prefix_split: ", prefix_split[0])

    if encap == "srv6":
        if service == "least_utilized":
            srv6_lu = srv6_util.srv6_util(prefix_split[0], dest_prefix)
        else:
            #srv6_ll = srv6_latency.low_latency_traverse(prefix_split[0], dest_prefix)
            srv6_ll = ext_latency.low_latency_traverse(prefix_split[0], dest_prefix)
    else:
        sr_ll = sr_latency.low_latency_traverse(prefix_split[0], dest_prefix)
    return 

if __name__ == '__main__':
    main()