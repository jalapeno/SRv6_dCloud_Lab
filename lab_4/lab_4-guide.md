## Intro to Jalapeno
### Configure BGP Monitoring Protocol (BMP), Streaming Telemetry, and install open-source Jalapeno package

R05
```
bmp server 1
 host 198.18.128.101 port 30511
 description jalapeno GoBMP  
 update-source MgmtEth0/RP0/CPU0/0
 flapping-delay 60
 initial-delay 5
 stats-reporting-period 60
 initial-refresh delay 25 spread 2
!
router bgp 65000
 neighbor 10.0.0.1
  bmp-activate server 1
 !
 neighbor fc00:0:1::1
  bmp-activate server 1
  !
 !
 neighbor 10.0.0.7
  bmp-activate server 1
 !
 neighbor fc00:0:7::1
  bmp-activate server 1
  !
 !
! 

```

R06
```
bmp server 1
 host 198.18.128.101 port 30511
 description jalapeno GoBMP  
 update-source MgmtEth0/RP0/CPU0/0
 flapping-delay 60
 initial-delay 5
 stats-reporting-period 60
 initial-refresh delay 25 spread 2
!
router bgp 65000
 neighbor 10.0.0.1
  bmp-activate server 1
 !
 neighbor fc00:0:1::1
  bmp-activate server 1
  !
 !
 neighbor 10.0.0.7
  bmp-activate server 1
 !
 neighbor fc00:0:7::1
  bmp-activate server 1
  !
 !
! 

```

Validate changes:
```
ping 198.18.128.101
show bgp bmp server 1
```

Expected output:
```
RP/0/RP0/CPU0:xrd06#ping 198.18.128.101
Wed Dec 14 23:00:18.649 UTC
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 198.18.128.101, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/7 ms

RP/0/RP0/CPU0:xrd06#sho bgp bmp ser 1  
Wed Dec 14 23:24:01.861 UTC
BMP server 1
Host 198.18.128.101 Port 30511
Connected for 00:01:18
...
```
### Install Jalapeno 

1. In a separate terminal session ssh to the Jalapeno VM 
```
cisco@198.18.1.101
pw = cisco123
```
2. Clone the Jalapeno repository at https://github.com/cisco-open/jalapeno and switch to the cleu-srv6-lab code branch:
```
git clone https://github.com/cisco-open/jalapeno.git
git checkout cleu-srv6-lab
```

3. Run the Jalapeno install script
```
cd jalapeno/install/
./deploy_jalapeno.sh 
```
Don't worry about the 'error validating' errors, they're cosmetic...we'll fix those one of these days

4. Verify k8s pods are running (note, some pods may initially be in a crashloop state. These should resolve after 2-3 minutes):
```
kubectl get pods -A
```
Expected output:
```
cisco@jalapeno:~/jalapeno/install$ kubectl get pods -A
NAMESPACE             NAME                                           READY   STATUS    RESTARTS        AGE
jalapeno-collectors   gobmp-5db68bd644-hzs82                         1/1     Running   3 (4m5s ago)    4m25s
jalapeno-collectors   telegraf-ingress-deployment-5b456574dc-wdhjk   1/1     Running   1 (4m2s ago)    4m25s
jalapeno              arangodb-0                                     1/1     Running   0               4m33s
jalapeno              grafana-deployment-565756bd74-x2szz            1/1     Running   0               4m32s
jalapeno              influxdb-0                                     1/1     Running   0               4m32s
jalapeno              kafka-0                                        1/1     Running   0               4m33s
jalapeno              lslinknode-edge-b954577f9-k8w6l                1/1     Running   4 (3m35s ago)   4m18s
jalapeno              telegraf-egress-deployment-5795ffdd9c-t8xrp    1/1     Running   2 (4m11s ago)   4m19s
jalapeno              topology-678ddb8bb4-rt9jg                      1/1     Running   3 (4m1s ago)    4m19s
jalapeno              zookeeper-0                                    1/1     Running   0               4m33s
kube-system           calico-kube-controllers-798cc86c47-d482k       1/1     Running   4 (16m ago)     14d
kube-system           calico-node-jd7cw                              1/1     Running   4 (16m ago)     14d
kube-system           coredns-565d847f94-fr8pp                       1/1     Running   4 (16m ago)     14d
kube-system           coredns-565d847f94-grmtl                       1/1     Running   4 (16m ago)     14d
kube-system           etcd-jalapeno                                  1/1     Running   5 (16m ago)     14d
kube-system           kube-apiserver-jalapeno                        1/1     Running   5 (16m ago)     14d
kube-system           kube-controller-manager-jalapeno               1/1     Running   6 (16m ago)     14d
kube-system           kube-proxy-pmwft                               1/1     Running   5 (16m ago)     14d
kube-system           kube-scheduler-jalapeno                        1/1     Running   6 (16m ago)     14d
```
5. Additional k8s commands:
```
kubectl get pods -n jalapeno
kubectl get pods -n jalapeno-collectors
kubectl get services -A
kubectl get all -A
kubectl get nodes
kubectl describe pod -n <namespace> <pod name>

example: kubectl describe pod -n jalapeno topology-678ddb8bb4-rt9jg
```
6. Install Jalapeno SR-Processors
```
cd ~/SRv6_dCloud_Lab/lab_4/
kubectl apply -f sr-node.yaml 
kubectl apply -f sr-topology.yaml 

kubectl get pods -n jalapeno

### Expected output:

cisco@jalapeno:~/sr-processors$ kubectl get pods -n jalapeno
NAME                                          READY   STATUS    RESTARTS      AGE
arangodb-0                                    1/1     Running   0             12m
grafana-deployment-565756bd74-x2szz           1/1     Running   0             12m
influxdb-0                                    1/1     Running   0             12m
kafka-0                                       1/1     Running   0             12m
lslinknode-edge-b954577f9-k8w6l               1/1     Running   4 (11m ago)   12m
sr-node-8487488c9f-ftj59                      1/1     Running   0             40s  <--
sr-topology-6b45d48c8-h8zns                   1/1     Running   0             33s  <--
telegraf-egress-deployment-5795ffdd9c-t8xrp   1/1     Running   2 (12m ago)   12m
topology-678ddb8bb4-rt9jg                     1/1     Running   3 (11m ago)   12m
zookeeper-0                                   1/1     Running   0             12m
```