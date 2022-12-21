import subprocess

def add_linux_route(dst, sid):
    subprocess.call(['sudo', 'ip', 'route', 'add', dst, 'encap', 'seg6', 'mode', 'encap', 'segs', sid, 'dev', 'ens192'])
    # sudo ip -6 route add 10.0.0.1/32 encap seg6 mode segs fc00:0:2:3:4:7:: dev ens192
    subprocess.call(['ip', 'route'])

def add_vpp_route(dst, sid):
    subprocess.call(['sudo', 'vppctl', 'ip route del', dst])
    subprocess.call(['sudo', 'vppctl', 'sr steer del l3', dst])
    subprocess.call(['sudo', 'vppctl', 'sr policy del bsid 101::101', dst])
    subprocess.call(['sudo', 'vppctl', 'sr', 'policy', 'add', 'bsid', '101::101', 'next', sid, 'encap'])
    subprocess.call(['sudo', 'vppctl', 'sr', 'steer', 'l3', dst, 'via', 'bsid', '101::101'])
    subprocess.call(['sudo', 'vppctl', 'show', 'ip', 'fib', dst])
