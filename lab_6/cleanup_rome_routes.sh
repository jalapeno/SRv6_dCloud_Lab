#/bin/bash

sudo ip route del 10.101.1.0/24  encap seg6 mode encap segs fc00:0:6:2:1::  dev ens192 scope link
sudo ip route del 10.101.1.0/24  encap seg6 mode encap segs fc00:0:6:5:1::  dev ens192 scope link
sudo ip route del 10.101.1.0/24  encap seg6 mode encap segs fc00:0:4:3:2:1::  dev ens192 scope link
sudo ip route del 10.101.1.0/24  encap seg6 mode encap segs fc00:0:4:5:1::  dev ens192 scope link
sudo ip route del 10.101.1.0/24  encap seg6 mode encap segs fc00:0:3:1::  dev ens192 scope link

sudo ip route del 10.0.0.1  encap seg6 mode encap segs fc00:0:6:2:1::  dev ens192 scope link
sudo ip route del 10.0.0.1  encap seg6 mode encap segs fc00:0:6:5:1::  dev ens192 scope link
sudo ip route del 10.0.0.1  encap seg6 mode encap segs fc00:0:4:3:2:1::  dev ens192 scope link
sudo ip route del 10.0.0.1  encap seg6 mode encap segs fc00:0:4:5:1::  dev ens192 scope link
sudo ip route del 10.0.0.1  encap seg6 mode encap segs fc00:0:3:1::  dev ens192 scope link

sudo ip route del 10.101.1.0/24 via 10.107.1.2 dev ens192
sudo ip route del 10.101.1.0/24 encap mpls 100006/100002/100001 via 10.107.1.2 dev ens192
sudo ip route del 10.101.1.0/24 encap mpls 100006/100005/100001 via 10.107.1.2 dev ens192
sudo ip route del 10.101.1.0/24 encap mpls 100004/100003/100002/100001 via 10.107.1.2 dev ens192
sudo ip route del 10.101.1.0/24 encap mpls 100004/100005/100001 via 10.107.1.2 dev ens192
sudo ip route del 10.101.1.0/24 encap mpls 100003/100001 via 10.107.1.2 dev ens192

sudo ip route del 10.0.0.1/32 encap mpls 100006/100002/100001 via 10.107.1.2 dev ens192
sudo ip route del 10.0.0.1/32 encap mpls 100006/100005/100001 via 10.107.1.2 dev ens192
sudo ip route del 10.0.0.1/32 encap mpls 100004/100003/100002/100001 via 10.107.1.2 dev ens192
sudo ip route del 10.0.0.1/32 encap mpls 100004/100005/100001 via 10.107.1.2 dev ens192
sudo ip route del 10.0.0.1/32 encap mpls 100003/100001 via 10.107.1.2 dev ens192