## Harvest SRv6 End.DT data into Arango

1. Configure streaming telemety on xrd01 and xrd07 using [this config](https://github.com/jalapeno/SRv6_dCloud_Lab/tree/lab7/lab_7/srv6-localsids/localsids/mdt.cfg)

2. On Jalapeno VM replace the Telegraf collector:

```
kubectl delete -f ~/jalapeno/install/collectors/telegraf-ingress/telegraf_ingress_cfg.yaml
kubectl delete -f ~/jalapeno/install/collectors/telegraf-ingress/telegraf_ingress_svc_np.yaml 
kubectl delete -f ~/jalapeno/install/collectors/telegraf-ingress/telegraf_ingress_dp.yaml 

kubectl create -f ~/SRv6_dCloud_Lab/lab_8/telegraf_ingress_cfg.yaml
kubectl create -f ~/jalapeno/install/collectors/telegraf-ingress/telegraf_ingress_svc_np.yaml 
kubectl create -f ~/jalapeno/install/collectors/telegraf-ingress/telegraf_ingress_dp.yaml 
```

3. Verify Telegraf ingress pod is running:
```
kubectl get pods -n jalapeno-collectors
```
```
cisco@jalapeno:~/SRv6_dCloud_Lab/lab_7/srv6-localsids/localsids$ kubectl get pods -n jalapeno-collectors
NAME                                           READY   STATUS    RESTARTS        AGE
gobmp-5db68bd644-2t6s7                         1/1     Running   9 (5h21m ago)   6d6h
telegraf-ingress-deployment-5b456574dc-ft4xm   1/1     Running   0               11s
```

4. Deploy the srv6-localsids-processor
```
cd ~/SRv6_dCloud_Lab/lab_7/srv6-localsids/localsids
python3 srv6-localsids-processor.py
```
Expected output:
```
document added:  xrd01_fc00:0:1111::
document added:  xrd01_fc00:0:1111:e000::
document added:  xrd01_fc00:0:1111:e001::
document added:  xrd01_fc00:0:1111:e002::
document added:  xrd01_fc00:0:1111:e003::
document added:  xrd01_fc00:0:1111:e004::
document added:  xrd01_fc00:0:1111:e005::
document added:  xrd01_fc00:0:1111:e006::
document added:  xrd01_fc00:0:1111:e007::
document added:  xrd01_fc00:0:1111:e008::
document added:  xrd01_fc00:0:1111:e009::
document added:  xrd07_fc00:0:7777::
document added:  xrd07_fc00:0:7777:e000::
document added:  xrd07_fc00:0:7777:e001::
document added:  xrd07_fc00:0:7777:e002::
document added:  xrd07_fc00:0:7777:e003::
document added:  xrd07_fc00:0:7777:e004::
document added:  xrd07_fc00:0:7777:e005::
document added:  xrd07_fc00:0:7777:e006::
document added:  xrd07_fc00:0:7777:e007::
```
5. Check that Arango as an *`srv6_local_sids`* data collection, and that it is populated
6. you can now kill the processor
```

```