import subprocess

def add_linux_route(dst, srv6_sid, prefix_sid, intf, encap):
    if encap == "srv6":
        print("adding linux SRv6 route: ip route add", dst, "encap seg6 mode encap segs", srv6_sid, "dev", intf)
        d = subprocess.call(['sudo', 'ip', 'route', 'del', dst])
        #a = subprocess.call(['sudo', 'ip', 'route', 'add', dst, 'encap', 'seg6', 'mode', 'encap', 'segs', 'fc00:0:6666:2222:1111:e008::', 'dev', intf])
        a = subprocess.call(['sudo', 'ip', 'route', 'add', dst, 'encap', 'seg6', 'mode', 'encap', 'segs', srv6_sid, 'dev', intf])
        print("Show Linux Route Table: ")
        subprocess.call(['ip', 'route'])

    if encap == "sr":
        label_stack = '/'.join([str(elem) for elem in prefix_sid])
        print("adding linux SR route: ip route add", dst, "encap mpls", label_stack, "via 10.107.1.2 dev", intf)
        a = subprocess.call(['sudo', 'ip', 'route', 'add', dst, 'encap', 'mpls', label_stack, 'via', '10.107.1.2', 'dev', intf])
        print("Show Linux Route Table: ")
        subprocess.call(['ip', 'route'])

def add_vpp_route(dst, srv6_sid, prefix_sid, encap):

    if encap == "srv6":
        print("adding vpp sr-policy to: ", dst, ", with SRv6 encap: ", srv6_sid)
        subprocess.call(['sudo', 'vppctl', 'ip route del', dst])
        subprocess.call(['sudo', 'vppctl', 'sr steer del l3', dst])
        subprocess.call(['sudo', 'vppctl', 'sr policy del bsid 101::101', dst])
        subprocess.call(['sudo', 'vppctl', 'sr', 'policy', 'add', 'bsid', '101::101', 'next', srv6_sid, 'encap'])
        subprocess.call(['sudo', 'vppctl', 'sr', 'steer', 'l3', dst, 'via', 'bsid', '101::101'])
        print("Display VPP FIB entry: ")
        subprocess.call(['sudo', 'vppctl', 'show', 'ip', 'fib', dst])

    if encap == "sr":
        print("adding vpp route to: ", dst, "with SR label stack", prefix_sid)
        label_stack = ' '.join([str(elem) for elem in prefix_sid])
        print("label stack: ", label_stack)
        subprocess.call(['sudo', 'vppctl', 'ip route del', dst])
        subprocess.call(['sudo', 'vppctl', 'sr steer del l3', dst])
        subprocess.call(['sudo', 'vppctl', 'sr policy del bsid 101::101', dst])
        subprocess.call(['sudo', 'vppctl', 'ip route add', dst, 'via 10.101.1.2 GigabitEthernetb/0/0 out-labels', label_stack])
        print("Display VPP FIB entry: ")
        subprocess.call(['sudo', 'vppctl', 'show', 'ip', 'fib', dst])