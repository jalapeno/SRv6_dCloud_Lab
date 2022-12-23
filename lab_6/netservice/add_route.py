import subprocess

def add_linux_route(dst, srv6_sid, prefix_sid, intf, encap):
    if encap == "srv6":
        print("adding linux route to: ", dst, ", with encap: ", srv6_sid, ", via dev: ", intf)
        p = subprocess.call(['sudo', 'ip', 'route', 'add', dst, 'encap', 'seg6', 'mode', 'encap', 'segs', srv6_sid, 'dev', intf])
        #sudo ip -6 route add 10.0.0.1/32 encap seg6 mode segs fc00:0:2:3:4:7:: dev ens192
        subprocess.call(['ip', 'route'])

    if encap == "sr":
        label_stack = ' '.join([str(elem) for elem in prefix_sid])
        print("adding linux route to: ", dst, ", with encap: ", label_stack, ", via dev: ", intf)
        #print("sudo ip route add ", dst, "encap mpls ", label_stack, "via 10.107.1.2 dev ", intf)
        p = subprocess.call(['sudo', 'ip', 'route', 'add', dst, 'encap', 'mpls', label_stack, 'via', '10.107.1.2', 'dev', intf])
        subprocess.call(['ip', 'route'])

    # print("adding linux route to: ", dst, ", with encap: ", srv6_sid, ", via dev: ", intf)
    # p = subprocess.call(['sudo', 'ip', 'route', 'add', dst, 'encap', 'seg6', 'mode', 'encap', 'segs', srv6_sid, 'dev', intf])
    # # sudo ip -6 route add 10.0.0.1/32 encap seg6 mode segs fc00:0:2:3:4:7:: dev ens192
    # subprocess.call(['ip', 'route'])

def add_vpp_route(dst, srv6_sid):
    print("adding vpp route/sr-policy to: ", dst, ", with encap: ", sid)
    subprocess.call(['sudo', 'vppctl', 'ip route del', dst])
    subprocess.call(['sudo', 'vppctl', 'sr steer del l3', dst])
    subprocess.call(['sudo', 'vppctl', 'sr policy del bsid 101::101', dst])
    subprocess.call(['sudo', 'vppctl', 'sr', 'policy', 'add', 'bsid', '101::101', 'next', srv6_sid, 'encap'])
    subprocess.call(['sudo', 'vppctl', 'sr', 'steer', 'l3', dst, 'via', 'bsid', '101::101'])
    subprocess.call(['sudo', 'vppctl', 'show', 'ip', 'fib', dst])


