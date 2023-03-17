#/bin/bash

result=$(bash -c 'sudo ip route del 10.101.2.0/24  encap seg6 mode encap segs fc00:0:6666:2222:1111::  dev ens192 scope link' 2>&1)
result=$(bash -c 'sudo ip route del 10.101.2.0/24  encap seg6 mode encap segs fc00:0:6666:5555:1111::  dev ens192 scope link' 2>&1)
result=$(bash -c 'sudo ip route del 10.101.2.0/24  encap seg6 mode encap segs fc00:0:4444:3333:2222:1111::  dev ens192 scope link' 2>&1)
result=$(bash -c 'sudo ip route del 10.101.2.0/24  encap seg6 mode encap segs fc00:0:4444:5555:1111::  dev ens192 scope link' 2>&1)
result=$(bash -c 'sudo ip route del 10.101.2.0/24  encap seg6 mode encap segs fc00:0:3333:1111::  dev ens192 scope link' 2>&1)
result=$(bash -c 'sudo ip route del 10.101.2.0/24  encap seg6 mode encap segs fc00:0:6666:2222:1111:e008:: dev ens192 scope link' 2>&1)

result=$(bash -c 'sudo ip route del 10.0.0.1  encap seg6 mode encap segs fc00:0:6666:2222:1111::  dev ens192 scope link' 2>&1)
result=$(bash -c 'sudo ip route del 10.0.0.1  encap seg6 mode encap segs fc00:0:6666:5555:1111:: dev ens192 scope link' 2>&1)
result=$(bash -c 'sudo ip route del 10.0.0.1  encap seg6 mode encap segs fc00:0:4444:3333:2222:1111::  dev ens192 scope link' 2>&1)
result=$(bash -c 'sudo ip route del 10.0.0.1  encap seg6 mode encap segs fc00:0:4444:5555:1111::  dev ens192 scope link' 2>&1)
result=$(bash -c 'sudo ip route del 10.0.0.1  encap seg6 mode encap segs fc00:0:3333:1111::  dev ens192 scope link' 2>&1)

result=$(bash -c 'sudo ip route del 10.101.2.0/24 via 10.107.1.2 dev ens192' 2>&1)
result=$(bash -c 'sudo ip route del 10.101.2.0/24 encap mpls 100006/100002/100001 via 10.107.1.2 dev ens192' 2>&1)
result=$(bash -c 'sudo ip route del 10.101.2.0/24 encap mpls 100006/100005/100001 via 10.107.1.2 dev ens192' 2>&1)
result=$(bash -c 'sudo ip route del 10.101.2.0/24 encap mpls 100004/100003/100002/100001 via 10.107.1.2 dev ens192' 2>&1)
result=$(bash -c 'sudo ip route del 10.101.2.0/24 encap mpls 100004/100005/100001 via 10.107.1.2 dev ens192' 2>&1)
result=$(bash -c 'sudo ip route del 10.101.2.0/24 encap mpls 100003/100001 via 10.107.1.2 dev ens192' 2>&1)

result=$(bash -c 'sudo ip route del 10.0.0.1/32 encap mpls 100006/100002/100001 via 10.107.1.2 dev ens192' 2>&1)
result=$(bash -c 'sudo ip route del 10.0.0.1/32 encap mpls 100006/100005/100001 via 10.107.1.2 dev ens192' 2>&1)
result=$(bash -c 'sudo ip route del 10.0.0.1/32 encap mpls 100004/100003/100002/100001 via 10.107.1.2 dev ens192' 2>&1)
result=$(bash -c 'sudo ip route del 10.0.0.1/32 encap mpls 100004/100005/100001 via 10.107.1.2 dev ens192' 2>&1)
result=$(bash -c 'sudo ip route del 10.0.0.1/32 encap mpls 100003/100001 via 10.107.1.2 dev ens192' 2>&1)
echo "Route cleanup complete"