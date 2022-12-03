1. Add proxy settings to /etc/environment

```
http_proxy=http://proxy.esl.cisco.com:8080
https_proxy=http://proxy.esl.cisco.com:8080
ftp_proxy=http://proxy.esl.cisco.com:8080
all_proxy=http://proxy.esl.cisco.com:8080
no_proxy=localhost,127.0.0.1,.cisco.com,.gspie.lab,10.200.96.74,10.200.96.120,mirror1,10.200.99.3,10.200.99.7,10.0.0.0/8,192.168.122.12,10.96.0.0/16,10.0.16.2,10.0.16.3
```
2. Logout and log back in

3. Disable swap
```
sudo swapoff -a 
sudo rm /swap.img
sudo vi /etc/fstab
  comment out the /swap.img line
```

4. If using Calico-VPP, edit netplan to add a VPP interface /etc/netplan/00-installer-config.yaml

```
network:
  ethernets:
    ens7:
      addresses:
        - 10.101.1.3/24
        - fc00:0:101:1::3/64
      routes:
        - to: 10.0.0.0/24
          via: 10.101.1.2
        - to: fc00:0000::/32
          via: fc00:0:101:1::2
        - to: 2001:420:ffff::/48
          via: fc00:0:101:1::2

```
5. sudo netplan apply

6. Install containerd
```
sudo apt install containerd
```

7. Containerd proxy setings
```
sudo mkdir /etc/systemd/system/containerd.service.d
sudo vi /etc/systemd/system/containerd.service.d/http-proxy.conf

Add this:

[Service]
Environment="http_proxy=http://proxy.esl.cisco.com:8080" 
Environment="https_proxy=http://proxy.esl.cisco.com:8080" 
Environment="no_proxy=localhost,127.0.0.1,127.0.0.0/8,.cisco.com,.gspie.lab,10.200.96.74,10.200.96.120,mirror1,10.200.99.0/24,10.200.99.7,10.0.0.0/8,192.168.122.23,10.96.0.0/16,10.0.16.2,10.0.16.3”
```

8. Restart containerd
```
sudo systemctl daemon-reload
sudo systemctl restart containerd

systemctl show --property=Environment containerd
```

9. Install k8s/kubeadm: https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/




