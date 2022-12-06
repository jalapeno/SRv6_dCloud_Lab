#/bin/sh

# this script was developed to setup Cisco Live SRv6 Lab environment
# it launches an XRd topology and a pair of Ubuntu VMs which it then 
# attaches to the topology 

echo "starting setup: " >> /home/ubuntu/startup.log

./xr-compose -f docker-compose-6-node.yml  -li localhost/ios-xr:7.8.1.18I
sudo sysctl -p
echo "sleeping for 10 seconds to let images build" >> /home/ubuntu/startup.log
sleep 10

docker network ls | awk -F': ' '/srv6_dcloud_lab_mgmt /{print $0}' > mgt_br.txt
mgt_br=$( head -n 1 mgt_br.txt | cut -c 1-12 )

echo "$mgt_br"
ifconfig br-"$mgt_br"

sudo /usr/bin/qemu-system-x86_64 -name guest=ubuntu-client,debug-threads=on \
-machine pc-i440fx-bionic,accel=tcg,usb=off,dump-guest-core=off -cpu qemu64 -m 1954 \
-overcommit mem-lock=off -smp 1,sockets=1,cores=1,threads=1 \
-uuid 3421fd71-7755-4822-9486-a97f91536f0a -no-user-config -nodefaults \
-global kvm-pit.lost_tick_policy=delay -no-hpet -no-reboot -global PIIX4_PM.disable_s3=1 \
-global PIIX4_PM.disable_s4=1 -boot strict=on \
-drive file=/home/cisco/images/ubuntu-client.qcow2,if=virtio,media=disk \
-device ich9-usb-ehci1,id=usb,bus=pci.0,addr=0x7.0x7 \
-device ich9-usb-uhci1,masterbus=usb.0,firstport=0,bus=pci.0,multifunction=on,addr=0x7 \
-device ich9-usb-uhci2,masterbus=usb.0,firstport=2,bus=pci.0,addr=0x7.0x1 \
-device ich9-usb-uhci3,masterbus=usb.0,firstport=4,bus=pci.0,addr=0x7.0x2 \
-device virtio-blk-pci,scsi=off,bus=pci.0,addr=0x5,drive=libvirt-1-format,id=virtio-disk0,bootindex=2 \
-netdev tap,fd=33,id=hostnet0 -device virtio-net-pci,netdev=hostnet0,id=net0,mac=52:54:00:0f:b0:c7,bus=pci.0,addr=0x3 \
-netdev tap,fd=34,id=hostnet1 -device virtio-net-pci,netdev=hostnet1,id=net1,mac=52:54:00:f9:4c:30,bus=pci.0,addr=0x4 \
-chardev pty,id=charserial0 -device isa-serial,chardev=charserial0,id=serial0 \
-device usb-tablet,id=input0,bus=usb.0,port=1 -vnc 0.0.0.0:0,password \
-device cirrus-vga,id=video0,bus=pci.0,addr=0x2 -device virtio-balloon-pci,id=balloon0,bus=pci.0,addr=0x6 \
-sandbox on,obsolete=deny,elevateprivileges=deny,spawn=deny,resourcecontrol=deny \
-msg timestamp=on

