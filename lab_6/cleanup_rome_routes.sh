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