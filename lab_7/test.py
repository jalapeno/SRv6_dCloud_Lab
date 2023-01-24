import argparse
### Jalapeno/SDN client ###

def main():
    # Handle cli options passed in
    parser = argparse.ArgumentParser(
        prog = 'Jalapeno client',
        description = 'takes command line input and calls path calculator functions',
        epilog = 'client.py -f <json file> -e <sr or srv6> -s <ll, lu, ds, or gp> ')
    parser.add_argument("-e", help="encapsulation type <sr> <srv6>")
    parser.add_argument("-f", help="json file with src, dst, parameters")  
    parser.add_argument("-s", help="requested network service: ll = low_latency, lu = least_utilized, ds = data_sovereignty, gp = get_paths)")
    args = parser.parse_args()

    encap = args.e
    file = args.f
    service = args.s

    # Check that the required input arguments were passed in
    if not encap or not file or not service:
        print("Required input elements encapsulation type, input file, and service type were not entered")
        print("client.py -f <json file> -e <sr or srv6> -s <ll, lu, ds, or gp>")
        exit()

    print("Passed through")

main()

