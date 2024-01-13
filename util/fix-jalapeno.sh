#!/bin/bash

echo "removing k8s components"
sudo apt-mark unhold kubeadm kubectl kubelet
sudo apt remove kubeadm kubectl kubelet -y
sudo systemctl daemon-reload

echo "re-install k8s components"
sudo apt install kubeadm=1.25.4-00 kubectl=1.25.4-00 kubelet=1.25.4-00
sudo apt-mark hold kubelet kubeadm kubectl
sudo modprobe bridge
sudo modprobe br_netfilter
sudo sysctl -p

echo "initializing cluster"
sudo kubeadm init
mkdir -p $HOME/.kube
rm $HOME/.kube/config
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

echo "verify cluster"
kubectl get nodes -o wide
kubectl get pods -A

echo "install Cilium CNI"
cilium install --version 1.14.5

sleep 10
echo "verify cluster and remove control plane taint"
kubectl get pods -A
kubectl taint nodes --all node-role.kubernetes.io/control-plane-


