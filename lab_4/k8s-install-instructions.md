## Reference: Kubernetes Install Instructions

#### instructions borrowed and edited from: https://thenewstack.io/how-to-deploy-kubernetes-with-kubeadm-and-containerd/

This document is for reference only and will not be used during the Cisco Live lab. Please feel free to refer to these instructions later if you are building your own K8s lab or cluster. These instructions have been verified on Ubuntu 20.04 and 22.04

1. turn off swap and set data/time:
```
sudo timedatectl set-timezone America/New_York
sudo swapoff -a
sudo rm /swap.img
```

2. Edit /etc/fstab, comment out swap
```
sudo nano /etc/fstab
```

3. apt update/upgrade
```
sudo apt update && sudo apt upgrade -y
```

4. add curl/https packages, keys, etc.
```
sudo apt install curl apt-transport-https -y
sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo chmod 644 /etc/apt/sources.list.d/kubernetes.list 
sudo apt update
```

5. apt install kubernetes packages:
``` 
sudo apt -y install kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

6. enable kubelet, modprobes:
```
sudo systemctl enable --now kubelet
sudo modprobe overlay
sudo modprobe br_netfilter
```
7. edit sysctl.conf
```
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding=1
```
```
sudo sysctl -p
```

8. install containerd and runc
```
wget https://github.com/containerd/containerd/releases/download/v2.0.0/containerd-2.0.0-linux-amd64.tar.gz 
wget https://raw.githubusercontent.com/containerd/containerd/main/containerd.service
sudo tar Cxzvf /usr/local containerd-2.0.0-linux-amd64.tar.gz 

sudo cp containerd.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now containerd

sudo systemctl status containerd

wget https://github.com/opencontainers/runc/releases/download/v1.2.1/runc.amd64
sudo  install -m 755 runc.amd64 /usr/local/sbin/runc
```

8. You may now initialize your k8s cluster with kubeadm init [reference](../readme.md#initialize-the-kubernetes-cluster)

9. Basic kubeadm init:
```
sudo kubeadm init
```

Or in the case of our lab:
```
sudo kubeadm init --config kubeadm-init.yaml
```

10. Copy admin.conf to user home directory:
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

10. Install Cilium CLI
```
CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/main/stable.txt)
CLI_ARCH=amd64
if [ "$(uname -m)" = "aarch64" ]; then CLI_ARCH=arm64; fi
curl -L --fail --remote-name-all https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-${CLI_ARCH}.tar.gz{,.sha256sum}
sha256sum --check cilium-linux-${CLI_ARCH}.tar.gz.sha256sum
sudo tar xzvfC cilium-linux-${CLI_ARCH}.tar.gz /usr/local/bin
rm cilium-linux-${CLI_ARCH}.tar.gz{,.sha256sum}
```

11. Install Cilium open source CNI (container Isovalent team to access Cilium Enterprise CNI)
```
cilium install
```

12. untaint control plane node:
```
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

 ## Back to Lab 4 Guide
[Lab 4 Guide](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/main/lab_4/lab_4-guide.md)